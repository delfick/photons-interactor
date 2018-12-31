from photons_interactor.commander.tiles import tile_dice, make_rgb_pixels, StyleMaker
from photons_interactor.commander import default_fields as df
from photons_interactor.commander.errors import NotAWebSocket
from photons_interactor.commander import helpers as chp
from photons_interactor.commander.store import store

from photons_app.errors import FoundNoDevices
from photons_app import helpers as hp

from photons_tile_paint.animation import (
      coords_for_horizontal_line
    , tile_serials_from_reference
    , canvas_to_msgs, orientations_from
    )
from photons_themes.coords import user_coords_to_pixel_coords
from photons_messages import DeviceMessages, TileMessages
from photons_themes.theme import ThemeColor as Color
from photons_control.tile import tiles_from
from photons_themes.canvas import Canvas

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from collections import defaultdict
from tornado import websocket
import logging

log = logging.getLogger("photons_interactor.commander.commands.tiles")

class ArrangeState:
    _merged_options_formattable = True

    def __init__(self):
        self.serials = {}
        self.style_maker = StyleMaker()

    async def start_arrange(self, serials, ref, target, afr):
        log.info(hp.lc("Starting arrange", serials=serials, ref=ref))
        all_errors = []

        for serial in list(self.serials):
            if serial not in serials:
                del self.serials[serial]

        for serial in serials:
            tasks = []
            refs = []
            pixels = None
            initial = None

            refs = defaultdict(list)

            if serial in self.serials:
                refs[serial] = self.serials[serial]["refs"]
                pixels = self.serials[serial]["pixels"]
                initial = self.serials[serial]["initial"]

            tasks.append((serial, hp.async_as_background(self.start(serial, target, afr, pixels, initial))))

            for serial, t in tasks:
                try:
                    errors, data = await t
                except Exception as error:
                    errors = [error]

                if errors:
                    all_errors.extend(errors)
                else:
                    initial, pixels, coords = data
                    self.serials[serial] = {"refs": refs[serial], "pixels": pixels, "initial": initial, "coords": coords}

        final = {"serials": {}}
        if all_errors:
            final["error"] = ", ".join(str(e) for e in all_errors)
            log.error(hp.lc("Failed to start arrange", errors=all_errors))

        for serial in serials:
            if serial in self.serials:
                if ref not in self.serials[serial]["refs"]:
                    self.serials[serial]["refs"].append(ref)
                final["serials"][serial] = self.info_for_browser(serial)

        return final

    def info_for_browser(self, serial):
        return {k: self.serials[serial][k] for k in ("pixels", "coords")}

    async def change(self, serial, tile_index, left_x, top_y, target, afr):
        if serial not in self.serials:
            return {"serial": serial, "data": None}

        user_x = (left_x + 4) / 8
        user_y = (top_y - 4) / 8

        msg = TileMessages.SetUserPosition(
              tile_index = tile_index
            , user_x = user_x
            , user_y = user_y
            , res_required = False
            )

        errors = []
        await target.script(msg).run_with_all(serial, afr, error_catcher=errors, timeout=5)

        if errors:
            return {"serial": serial, "data": None}

        coords = []
        get_chain = TileMessages.GetDeviceChain()
        async for pkt, _, _ in target.script(get_chain).run_with(serial, afr, error_catcher=errors, timeout=5):
            if pkt | TileMessages.StateDeviceChain:
                coords = [((c.user_x, c.user_y), (c.width, c.height)) for c in tiles_from(pkt)]
                coords = [top_left for top_left, _ in user_coords_to_pixel_coords(coords)]
                self.serials[serial]["coords"] = coords

        return {"serial": serial, "data": self.info_for_browser(serial)}

    async def leave_arrange(self, ref, target, afr):
        log.info(hp.lc("Leaving arrange", ref=ref))

        tasks = []

        for serial, info in list(self.serials.items()):
            info["refs"] = [r for r in info["refs"] if r != ref]
            if not info["refs"]:
                tasks.append(hp.async_as_background(self.restore(serial, info["initial"], target, afr)))
                del self.serials[serial]

        for t in tasks:
            await t

    async def start(self, serial, target, afr, pixels, initial):
        length = 5
        errors = []
        coords = []
        orientations = []

        msgs = [TileMessages.GetDeviceChain()]
        if initial is None:
            initial = {"colors": [], "power": 65535}
            msgs.append(TileMessages.GetState64(tile_index=0, length=5, x=0, y=0, width=8))
            msgs.append(DeviceMessages.GetPower())

        async for pkt, _, _ in target.script(msgs).run_with(serial, afr, error_catcher=errors):
            if pkt | TileMessages.State64:
                initial["colors"].append(
                      [ {"hue": c.hue, "saturation": c.saturation, "brightness": c.brightness, "kelvin":  c.kelvin}
                        for c in pkt.colors
                      ]
                    )
            elif pkt | TileMessages.StateDeviceChain:
                length = pkt.total_count
                orientations = orientations_from(pkt)
                coords = [((c.user_x, c.user_y), (c.width, c.height)) for c in tiles_from(pkt)]
                coords = [top_left for top_left, _ in user_coords_to_pixel_coords(coords)]
            elif pkt | DeviceMessages.StatePower:
                initial["power"] = pkt.level

        if errors:
            return errors, None, None

        if pixels is None:
            canvas = Canvas()

            def dcf(i, j):
                return Color(0, 0, 0, 3500)
            canvas.default_color_func = dcf

            self.style_maker.set_canvas(canvas, length)
            pixels = make_rgb_pixels(canvas, length)

            msgs = [DeviceMessages.SetPower(level=65535)]
            msgs.extend(canvas_to_msgs(canvas, coords_for_horizontal_line, duration=1, acks=True, orientations=orientations))
            await target.script(msgs).run_with_all(serial, afr, error_catcher=errors)

            if errors:
                return errors, None

        return errors, (initial, pixels, coords)

    async def restore(self, serial, initial, target, afr):
        msgs = [DeviceMessages.SetPower(level=initial["power"])]

        for i, colors in enumerate(initial["colors"]):
            msgs.append(TileMessages.SetState64(
                  tile_index = i
                , length = 1
                , width = 8
                , x = 0
                , y = 0
                , colors = colors
                , res_required = False
                , ack_required = True
                ))

        def errors(e):
            log.error(hp.lc("Error restoring tile", serial=serial, error=e))
        await target.script(msgs).run_with_all(serial, afr, error_catcher=errors)

@store.command(name="tiles/dice")
class TileDiceCommand(store.Command):
    """
    Show dice on provided tiles and return the hsbk values that were sent
    """
    finder = store.injected("finder")
    target = store.injected("targets.lan")

    matcher = df.matcher_field
    refresh = df.refresh_field

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)

        result = chp.ResultBuilder()
        afr = await self.finder.args_for_run()
        reference = self.finder.find(filtr=fltr)

        serials = await tile_serials_from_reference(self.target, reference, afr)
        if not serials:
            raise FoundNoDevices("Didn't find any tiles")

        await self.target.script(DeviceMessages.SetPower(level=65535)).run_with_all(serials, afr
            , error_catcher = result.error
            )

        result.result["results"]["tiles"] = await tile_dice(self.target, serials, afr
            , error_catcher = result.error
            )

        return result

@store.command(name="tiles/arrange/start")
class StartArrangeCommand(store.Command):
    finder = store.injected("finder")
    target = store.injected("targets.lan")
    arranger = store.injected("arranger")
    request_handler = store.injected("request_handler")

    async def execute(self):
        if not isinstance(self.request_handler, websocket.WebSocketHandler):
            raise NotAWebSocket()

        afr = await self.finder.args_for_run()
        serials = await tile_serials_from_reference(self.target, self.finder.find(), afr)
        return await self.arranger.start_arrange(serials, self.request_handler.key, self.target, afr)

@store.command(name="tiles/arrange/leave")
class LeaveArrangeCommand(store.Command):
    finder = store.injected("finder")
    target = store.injected("targets.lan")
    arranger = store.injected("arranger")
    request_handler = store.injected("request_handler")

    async def execute(self):
        if not isinstance(self.request_handler, websocket.WebSocketHandler):
            raise NotAWebSocket()

        afr = await self.finder.args_for_run()
        await self.arranger.leave_arrange(self.request_handler.key, self.target, afr)
        return {"ok": True}

@store.command(name="tiles/arrange/change")
class ChangeArrangeCommand(store.Command):
    finder = store.injected("finder")
    target = store.injected("targets.lan")
    arranger = store.injected("arranger")

    serial = dictobj.Field(sb.string_spec)
    tile_index = dictobj.Field(sb.integer_spec)
    left_x = dictobj.Field(sb.integer_spec)
    top_y = dictobj.Field(sb.integer_spec)

    async def execute(self):
        afr = await self.finder.args_for_run()
        return await self.arranger.change(self.serial, self.tile_index, self.left_x, self.top_y, self.target, afr)

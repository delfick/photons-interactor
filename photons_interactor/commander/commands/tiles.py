from photons_interactor.commander.tiles import tile_dice, make_rgb_pixels, StyleMaker
from photons_interactor.commander import default_fields as df
from photons_interactor.commander.errors import NotAWebSocket
from photons_interactor.commander import helpers as chp
from photons_interactor.commander.store import store

from photons_app import helpers as hp

from photons_tile_paint.animation import (
      coords_for_horizontal_line
    , tile_serials_from_reference
    , canvas_to_msgs, orientations_from
    )
from photons_messages import DeviceMessages, TileMessages
from photons_themes.theme import ThemeColor as Color
from photons_themes.canvas import Canvas

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
        for serial in serials:
            tasks = []
            if serial not in self.serials:
                tasks.append((serial, hp.async_as_background(self.start(serial, target, afr))))

            for serial, t in tasks:
                try:
                    errors, initial, pixels = await t
                except Exception as error:
                    errors = [error]

                if errors:
                    all_errors.extend(errors)

                if pixels:
                    self.serials[serial] = {"refs": [], "pixels": pixels, "initial": initial}

        final = {"serials": {}}
        if all_errors:
            final["error"] = ", ".join(str(e) for e in all_errors)
            log.error(hp.lc("Failed to start arrange", errors=all_errors))

        for serial in serials:
            if serial in self.serials:
                if ref not in self.serials[serial]["refs"]:
                    self.serials[serial]["refs"].append(ref)
                final["serials"][serial] = self.serials[serial]["pixels"]

        return final

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

    async def start(self, serial, target, afr):
        length = 5
        errors = []
        initial = {"colors": [], "power": 65535}
        orientations = []

        get_state = TileMessages.GetState64(tile_index=0, length=5, x=0, y=0, width=8)
        get_chain = TileMessages.GetDeviceChain()
        get_power = DeviceMessages.GetPower()
        async for pkt, _, _ in target.script([get_state, get_chain, get_power]).run_with(serial, afr, error_catcher=errors):
            if pkt | TileMessages.State64:
                initial["colors"].append(
                      [ {"hue": c.hue, "saturation": c.saturation, "brightness": c.brightness, "kelvin":  c.kelvin}
                        for c in pkt.colors
                      ]
                    )
            elif pkt | TileMessages.StateDeviceChain:
                length = pkt.total_count
                orientations = orientations_from(pkt)
            elif pkt | DeviceMessages.StatePower:
                initial["power"] = pkt.level

        if errors:
            return errors, None, None

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
            return errors, None, None

        return errors, initial, pixels

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

        await self.target.script(DeviceMessages.SetPower(level=65535)).run_with_all(reference, afr
            , error_catcher = result.error
            )

        result.result["results"]["tiles"] = await tile_dice(self.target, self.finder.find(filtr=fltr), afr
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

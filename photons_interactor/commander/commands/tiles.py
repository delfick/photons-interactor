from photons_interactor.commander.tiles import tile_dice, make_rgb_and_color_pixels, StyleMaker
from photons_interactor.commander import default_fields as df
from photons_interactor.commander.errors import NotAWebSocket
from photons_interactor.commander import helpers as chp
from photons_interactor.commander.store import store

from photons_app.errors import FoundNoDevices
from photons_app import helpers as hp

from photons_tile_paint.animation import (
    coords_for_horizontal_line,
    tile_serials_from_reference,
    canvas_to_msgs,
)
from photons_themes.coords import user_coords_to_pixel_coords
from photons_messages import DeviceMessages, TileMessages
from photons_control.planner import Gatherer, make_plans
from photons_themes.theme import ThemeColor as Color
from photons_control.planner.plans import ChainPlan
from photons_themes.canvas import Canvas

from delfick_project.norms import dictobj, sb
from tornado import websocket
import logging
import asyncio

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

            info = {"refs": [], "highlightlock": asyncio.Lock()}
            if serial in self.serials:
                info = self.serials[serial]

            tasks.append((serial, hp.async_as_background(self.start(serial, info, target, afr))))

            for serial, t in tasks:
                try:
                    errors, data = await t
                except Exception as error:
                    errors = [error]

                if errors:
                    all_errors.extend(errors)
                else:
                    info.update(data)
                    self.serials[serial] = info

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
            tile_index=tile_index, user_x=user_x, user_y=user_y, res_required=False
        )

        errors = []
        await target.script(msg).run_with_all(serial, afr, error_catcher=errors, message_timeout=5)
        hp.async_as_background(
            self.highlight(serial, tile_index, target, afr, error_catcher=[], message_timeout=3)
        )

        if errors:
            return {"serial": serial, "data": None}

        plans = make_plans(chain=ChainPlan(refresh=True))
        gatherer = Gatherer(target)

        got = await gatherer.gather_all(plans, serial, afr, error_catcher=errors, message_timeout=5)

        if serial in got and got[serial][0]:
            pixel_coords = user_coords_to_pixel_coords(got[serial][1]["chain"]["coords_and_sizes"])
            self.serials[serial]["coords"] = [xy for xy, _ in pixel_coords]

        return {"serial": serial, "data": self.info_for_browser(serial)}

    async def highlight(
        self, serial, tile_index, target, afr, error_catcher=None, message_timeout=3
    ):
        if serial not in self.serials or self.serials[serial]["highlightlock"].locked():
            return

        async with self.serials[serial]["highlightlock"]:
            if serial not in self.serials:
                return

            passed = 0
            row = -1
            pixels = self.serials[serial]["color_pixels"][tile_index]
            reorient = self.serials[serial]["reorient"]

            while passed < 2 and not afr.stop_fut.done():
                colors = []
                for i in range(8):
                    if row < i:
                        start = i * 8
                        colors.extend(pixels[start : start + 8])
                    else:
                        colors.extend(
                            [{"hue": 0, "saturation": 0, "brightness": 0, "kelvin": 3500}] * 8
                        )

                msg = TileMessages.Set64(
                    tile_index=tile_index,
                    length=1,
                    x=0,
                    y=0,
                    width=8,
                    colors=reorient(tile_index, colors),
                    res_required=False,
                    ack_required=False,
                )

                await target.script(msg).run_with_all(serial, afr, error_catcher=[])
                await asyncio.sleep(0.075)

                if passed == 0:
                    row += 3
                    if row > 7:
                        passed += 1
                else:
                    row -= 3
                    if row < 0:
                        passed += 1

            if not afr.stop_fut.done():
                msg = TileMessages.Set64(
                    tile_index=tile_index,
                    length=1,
                    x=0,
                    y=0,
                    width=8,
                    colors=reorient(tile_index, pixels),
                    res_required=False,
                    ack_required=True,
                )
                await target.script(msg).run_with_all(
                    serial, afr, error_catcher=[], message_timeout=1
                )

    async def leave_arrange(self, ref, target, afr):
        log.info(hp.lc("Leaving arrange", ref=ref))

        tasks = []

        for serial, info in list(self.serials.items()):
            info["refs"] = [r for r in info["refs"] if r != ref]
            if not info["refs"]:
                tasks.append(
                    hp.async_as_background(self.restore(serial, info["initial"], target, afr))
                )
                del self.serials[serial]

        for t in tasks:
            await t

    async def start(self, serial, info, target, afr):
        errors = []

        plans = ["chain"]
        if info.get("initial") is None:
            info["initial"] = {"colors": [], "power": 65535}
            plans.append("colors")
            plans.append("power")

        plans = make_plans(*plans)
        gatherer = Gatherer(target)

        got = await gatherer.gather_all(plans, serial, afr, error_catcher=errors)
        if errors:
            return errors, info

        chain = got[serial][1]["chain"]
        power = got[serial][1].get("power")
        colors = got[serial][1].get("colors")

        if power is not None:
            info["initial"]["power"] = power["level"]
        if colors is not None:
            info["initial"]["colors"] = colors

        pixel_coords = user_coords_to_pixel_coords(chain["coords_and_sizes"])
        info["coords"] = [top_left for top_left, _ in pixel_coords]
        info["reorient"] = chain["reorient"]

        if info.get("pixels") is None:
            canvas = Canvas()

            def dcf(i, j):
                return Color(0, 0, 0, 3500)

            canvas.default_color_func = dcf

            length = len(info["coords"])
            self.style_maker.set_canvas(canvas, length)
            info["pixels"], info["color_pixels"] = make_rgb_and_color_pixels(canvas, length)

            msgs = [DeviceMessages.SetPower(level=65535)]
            msgs.extend(
                canvas_to_msgs(
                    canvas,
                    coords_for_horizontal_line,
                    duration=1,
                    acks=True,
                    reorient=info["reorient"],
                )
            )
            await target.script(msgs).run_with_all(serial, afr, error_catcher=errors)

        return errors, info

    async def restore(self, serial, initial, target, afr):
        msgs = [DeviceMessages.SetPower(level=initial["power"])]

        for i, colors in enumerate(initial["colors"]):
            msgs.append(
                TileMessages.Set64(
                    tile_index=i,
                    length=1,
                    width=8,
                    x=0,
                    y=0,
                    colors=colors,
                    res_required=False,
                    ack_required=True,
                )
            )

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

        await self.target.script(DeviceMessages.SetPower(level=65535)).run_with_all(
            serials, afr, error_catcher=result.error
        )

        result.result["results"]["tiles"] = await tile_dice(
            self.target, serials, afr, error_catcher=result.error
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
        return await self.arranger.start_arrange(
            serials, self.request_handler.key, self.target, afr
        )


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

    serial = dictobj.Field(sb.string_spec, wrapper=sb.required)
    tile_index = dictobj.Field(sb.integer_spec, wrapper=sb.required)
    left_x = dictobj.Field(sb.integer_spec, wrapper=sb.required)
    top_y = dictobj.Field(sb.integer_spec, wrapper=sb.required)

    async def execute(self):
        afr = await self.finder.args_for_run()
        return await self.arranger.change(
            self.serial, self.tile_index, self.left_x, self.top_y, self.target, afr
        )


@store.command(name="tiles/arrange/highlight")
class HighlightArrangeCommand(store.Command):
    finder = store.injected("finder")
    target = store.injected("targets.lan")
    arranger = store.injected("arranger")

    serial = dictobj.Field(sb.string_spec, wrapper=sb.required)
    tile_index = dictobj.Field(sb.integer_spec, wrapper=sb.required)

    async def execute(self):
        afr = await self.finder.args_for_run()
        await self.arranger.highlight(self.serial, self.tile_index, self.target, afr)
        return {"ok": True}

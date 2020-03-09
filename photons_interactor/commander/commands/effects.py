from photons_interactor.commander import default_fields as df
from photons_interactor.commander import helpers as chp
from photons_interactor.commander.store import store

from photons_themes.addon import ApplyTheme, default_colors, Options as ThemeOptions
from photons_messages.enums import TileEffectType, MultiZoneEffectType
from photons_control.planner import Gatherer, make_plans, Skip
from photons_control.script import FromGeneratorPerSerial
from photons_control.multizone import SetZonesEffect
from photons_control.tile import SetTileEffect
from photons_protocol.types import enum_spec
from photons_products.base import Product

from delfick_project.norms import dictobj, sb, Meta
from enum import Enum


class EffectCommand(store.Command):
    finder = store.injected("finder")
    target = store.injected("targets.lan")

    timeout = df.timeout_field
    matcher = df.matcher_field
    refresh = df.refresh_field

    apply_theme = dictobj.Field(
        sb.boolean,
        default=False,
        help="Whether to apply a theme to the devices before running an animation",
    )
    theme_options = dictobj.Field(
        sb.dictionary_spec, help="Any options to give to applying a theme"
    )

    def theme_msg(self, gatherer):
        everything = {}
        theme_options = dict(self.theme_options)

        if "overrides" in theme_options:
            everything["overrides"] = theme_options["overrides"]

        if "colors" not in theme_options:
            theme_options["colors"] = default_colors

        options = ThemeOptions.FieldSpec().normalise(Meta(everything, []), theme_options)
        return ApplyTheme.script(options, gatherer=gatherer)


@store.command(name="effects/run")
class RunEffectCommand(EffectCommand):
    """
    Start or stop a firmware animation on devices that support them
    """

    matrix_animation = dictobj.NullableField(
        enum_spec(None, TileEffectType, unpacking=True),
        help="""
            The animation to run for matrix devices.

            This can be FLAME, MORPH or OFF.

            If you don't supply this these devices will not run any animation"
        """,
    )
    matrix_options = dictobj.Field(
        sb.dictionary_spec,
        help="""
                Any options to give to the matrix animation. For example duration
            """,
    )

    linear_animation = dictobj.NullableField(
        enum_spec(None, MultiZoneEffectType, unpacking=True),
        help="""
            The animation to run for linear devices.

            Currently only MOVE or OFF are supported

            If you don't supply this these devices will not run any animation"
        """,
    )
    linear_options = dictobj.Field(
        sb.dictionary_spec,
        help="""
                Any options to give to the linear animation. For example duration
            """,
    )

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher)

        if self.refresh is not None:
            fltr.force_refresh = self.refresh

        gatherer = Gatherer(self.target)
        theme_msg = self.theme_msg(gatherer)

        async def gen(reference, afr, **kwargs):
            if self.apply_theme:
                yield theme_msg

            if self.matrix_animation:
                yield SetTileEffect(self.matrix_animation, gatherer=gatherer, **self.matrix_options)

            if self.linear_animation:
                yield SetZonesEffect(
                    self.linear_animation, gatherer=gatherer, **self.linear_options
                )

        script = self.target.script(FromGeneratorPerSerial(gen))
        return await chp.run(
            script, fltr, self.finder, message_timeout=self.timeout, add_replies=False,
        )


@store.command(name="effects/stop")
class StopEffectCommand(EffectCommand):
    """
    Stop any firmware effects on devices.
    """

    stop_matrix = dictobj.Field(
        sb.boolean, default=True, help="Whether to stop any matrix animations"
    )
    stop_linear = dictobj.Field(
        sb.boolean, default=True, help="Whether to stop any linear animations"
    )

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher)

        if self.refresh is not None:
            fltr.force_refresh = self.refresh

        gatherer = Gatherer(self.target)
        theme_msg = self.theme_msg(gatherer)

        async def gen(reference, afr, **kwargs):
            if self.apply_theme:
                yield theme_msg

            if self.stop_matrix:
                yield SetTileEffect(TileEffectType.OFF, gatherer=gatherer, palette=[])

            if self.stop_linear:
                yield SetZonesEffect(MultiZoneEffectType.OFF, gatherer=gatherer)

        script = self.target.script(FromGeneratorPerSerial(gen))
        return await chp.run(
            script, fltr, self.finder, message_timeout=self.timeout, add_replies=False,
        )


@store.command(name="effects/status")
class StatusEffectCommand(store.Command):
    """
    Returns the current status of effects on devices that support them
    """
    finder = store.injected("finder")
    target = store.injected("targets.lan")

    timeout = df.timeout_field
    matcher = df.matcher_field
    refresh = df.refresh_field

    def convert_enums(self, info):
        if isinstance(info, Product):
            info = {
                "pid": info.pid,
                "vid": info.vendor.vid,
                "cap": info.cap.as_dict(),
                "name": info.name,
            }

        if info is Skip:
            return {"type": "SKIP"}
        elif isinstance(info, dict):
            result = {}
            for k, v in info.items():
                result[k] = self.convert_enums(v)
            return result
        elif isinstance(info, list):
            return [self.convert_enums(i) for i in info]
        elif isinstance(info, Enum):
            return info.name
        else:
            return info

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher)

        if self.refresh is not None:
            fltr.force_refresh = self.refresh

        gatherer = Gatherer(self.target)
        plans = make_plans("firmware_effects", "capability")

        afr = await self.finder.args_for_run()
        serials = await self.finder.serials(filtr=fltr)

        result = chp.ResultBuilder()
        result.add_serials(serials)

        async for serial, _, info in gatherer.gather_per_serial(
            plans, serials, afr, error_catcher=result.error, message_timeout=self.timeout,
        ):
            r = {}
            if "capability" in info:
                r["product"] = info["capability"]["product"]
            if "firmware_effects" in info:
                r["effect"] = info["firmware_effects"]
            result.result["results"][serial] = self.convert_enums(r)

        return result

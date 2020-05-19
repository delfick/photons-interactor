from photons_interactor.commander import default_fields as df
from photons_interactor.commander import helpers as chp
from photons_interactor.commander.store import store

from photons_control.transform import Transformer, PowerToggle

from delfick_project.norms import dictobj, sb


@store.command(name="status")
class StatusCommand(store.Command):
    """
    Return "on": true
    """
    async def execute(self):
        return {"on": True}


@store.command(name="discover")
class DiscoverCommand(store.Command):
    """
    Display information about all the devices that can be found on the network
    """

    finder = store.injected("finder")
    matcher = df.matcher_field
    refresh = df.refresh_field

    just_serials = dictobj.Field(
        sb.boolean,
        default=False,
        help="Just return a list of serials instead of all the information per device",
    )

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher)

        if self.refresh is not None:
            fltr.force_refresh = self.refresh

        if self.just_serials:
            return await self.finder.serials(filtr=fltr)
        else:
            return await self.finder.info_for(filtr=fltr)


@store.command(name="query")
class QueryCommand(store.Command):
    """
    Send a pkt to devices and return the result
    """

    finder = store.injected("finder")
    target = store.injected("targets.lan")
    protocol_register = store.injected("protocol_register")

    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field

    pkt_type = df.pkt_type_field
    pkt_args = df.pkt_args_field

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = chp.make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, message_timeout=self.timeout)


@store.command(name="power_toggle")
class PowerToggleCommand(store.Command):
    """
    Toggle the power of the lights you specify
    """

    finder = store.injected("finder")
    target = store.injected("targets.lan")

    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field

    duration = dictobj.NullableField(sb.float_spec)

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)

        kwargs = {}
        if self.duration:
            kwargs["duration"] = self.duration
        msg = PowerToggle(**kwargs)

        script = self.target.script(msg)
        return await chp.run(
            script, fltr, self.finder, add_replies=False, message_timeout=self.timeout
        )


@store.command(name="transform")
class TransformCommand(store.Command):
    """
    Apply a http api like transformation to the lights
    """

    finder = store.injected("finder")
    target = store.injected("targets.lan")

    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field

    transform = dictobj.Field(
        sb.dictionary_spec(),
        wrapper=sb.required,
        help="""
            A dictionary of what options to use to transform the lights with.

            For example,
            ``{"power": "on", "color": "red"}``

            Or,
            ``{"color": "blue", "effect": "breathe", "cycles": 5}``
          """,
    )

    transform_options = dictobj.Field(
        sb.dictionary_spec(),
        help="""
            A dictionay of options that modify the way the tranform
            is performed:

            keep_brightness
                Ignore brightness options in the request

            transition_color
                If the light is off and we power on, setting this to True will mean the
                color of the light is not set to the new color before we make it appear
                to be on. This defaults to False, which means it will appear to turn on
                with the new color
            """,
    )

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = Transformer.using(self.transform, **self.transform_options)
        script = self.target.script(msg)
        return await chp.run(
            script, fltr, self.finder, add_replies=False, message_timeout=self.timeout
        )


@store.command(name="set")
class SetCommand(store.Command):
    """
    Send a pkt to devices. This is the same as query except res_required is False
    and results aren't returned
    """

    finder = store.injected("finder")
    target = store.injected("targets.lan")
    protocol_register = store.injected("protocol_register")

    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field

    pkt_type = df.pkt_type_field
    pkt_args = df.pkt_args_field

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = chp.make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        msg.res_required = False
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, message_timeout=self.timeout)

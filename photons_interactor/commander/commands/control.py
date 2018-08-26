from photons_interactor.commander.commands.base import Command
from photons_interactor.commander import default_fields as df
from photons_interactor.commander.decorator import command
from photons_interactor.commander import helpers as chp

from photons_transform.transformer import Transformer

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb

@command(name="discover")
class DiscoverCommand(Command):
    """
    Display information about all the devices that can be found on the network
    """
    finder = df.finder_field
    matcher = df.matcher_field
    refresh = df.refresh_field

    just_serials = dictobj.Field(sb.boolean, default=False
        , help = "Just return a list of serials instead of all the information per device"
        )

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher)

        if self.refresh is not None:
            fltr.force_refresh = self.refresh

        if self.just_serials:
            return await self.finder.serials(filtr=fltr)
        else:
            return await self.finder.info_for(filtr=fltr)

@command(name="query")
class QueryCommand(Command):
    """
    Send a pkt to devices and return the result
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field
    protocol_register = df.protocol_register_field

    pkt_type = df.pkt_type_field
    pkt_args = df.pkt_args_field

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = chp.make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, timeout=self.timeout)

@command(name="transform")
class TransformCommand(Command):
    """
    Apply a http api like transformation to the lights
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field

    transform = dictobj.Field(sb.dictionary_spec(), wrapper=sb.required
        , help = """
            A dictionary of what options to use to transform the lights with.

            For example,
            ``{"power": "on", "color": "red"}``

            Or,
            ``{"color": "blue", "effect": "breathe", "cycles": 5}``
          """
        )

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = Transformer.using(self.transform)
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, add_replies=False, timeout=self.timeout)

@command(name="set")
class SetCommand(Command):
    """
    Send a pkt to devices. This is the same as query except res_required is False
    and results aren't returned
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field
    protocol_register = df.protocol_register_field

    pkt_type = df.pkt_type_field
    pkt_args = df.pkt_args_field

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = chp.make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        msg.res_required = False
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, timeout=self.timeout)

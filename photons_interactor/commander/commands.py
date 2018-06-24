from photons_interactor.commander.decorator import command, available_commands
from photons_interactor.commander.errors import NoSuchCommand
from photons_interactor.commander import default_fields as df
from photons_interactor.commander import helpers as chp

from photons_transform.transformer import Transformer

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from textwrap import dedent

class Command(dictobj.Spec):
    async def execute(self):
        raise NotImplementedError("Base command has no execute implementation")

@command(name="help")
class HelpCommand(Command):
    """
    Display the documentation for the specified command

    command: help
    args:
      command: string - command to display help for
    """
    command = dictobj.Field(sb.string_spec, default="help")

    async def execute(self):
        if self.command not in available_commands:
            raise NoSuchCommand(wanted=self.command, available=sorted(available_commands))
        header = f"Command {self.command}"
        doc = dedent(available_commands[self.command]["kls"].__doc__)
        extra = ""
        if self.command == "help":
            extra = "\nAvailable commands:\n{}".format(
                  "\n".join(f" * {name}" for name in sorted(available_commands))
                )
        return f"{header}\n{'=' * len(header)}\n\n{doc}{extra}"

@command(name="discover")
class DiscoverCommand(Command):
    """
    Display information about all the devices that can be found on the network

    command: discover
    args:
        refresh: bool (default False) - Do a fresh search for devices
        just_serials: bool (default False) - Just return the serials
        matcher: string or dict (default None) - Specific devices to search for
    """
    finder = df.finder_field
    matcher = df.matcher_field
    refresh = df.refresh_field
    just_serials = dictobj.Field(sb.boolean, default=False)

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

    command: query
    args:
        refresh: bool (default False) - Do a fresh search for devices
        multiple: bool (default False) - Expect multiple replies for each packet
        matcher: string or dict (default None) - Specific devices to search for
        timeout: integer (default 20) - Seconds to wait for replies to the packets
        pkt_type: int or string (required) - The pkt type to send to the lights (i.e. 101 or "GetColor")
        pkt_args: dict (optional) - Any arguments the pkt requires in it's payload
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field
    multiple = dictobj.Field(sb.boolean, default=False)
    protocol_register = df.protocol_register_field

    pkt_type = dictobj.Field(sb.or_spec(sb.integer_spec(), sb.string_spec()), wrapper=sb.required)
    pkt_args = dictobj.NullableField(sb.dictionary_spec())

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = chp.make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, timeout=self.timeout, multiple_replies=self.multiple)

@command(name="transform")
class TransformCommand(Command):
    """
    Apply a http api like transformation to the lights

    command: transform
    args:
        refresh: bool (default False) - Do a fresh search for devices
        matcher: string or dict (default None) - Specific devices to search for
        timeout: integer (default 20) - Seconds to wait for replies to the packets
        transform: dict - The transformation to apply
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field

    transform = dictobj.Field(sb.dictionary_spec(), wrapper=sb.required)

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = Transformer.using(self.transform)
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, add_replies=False, timeout=self.timeout)

@command(name="set")
class SetCommand(Command):
    """
    Send a pkt to devices. This is the same as query except res_required is False and results aren't returned

    command: set
    args:
        refresh: bool (default False) - Do a fresh search for devices
        matcher: string or dict (default None) - Specific devices to search for
        timeout: integer (default 20) - Seconds to wait for replies to the packets
        pkt_type: int or string (required) - The pkt type to send to the lights (i.e. 117 or "SetPower")
        pkt_args: dict (optional) - Any arguments the pkt requires in it's payload
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field
    protocol_register = df.protocol_register_field

    pkt_type = dictobj.Field(sb.or_spec(sb.integer_spec(), sb.string_spec()), wrapper=sb.required)
    pkt_args = dictobj.NullableField(sb.dictionary_spec())

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = chp.make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        msg.res_required = False
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, timeout=self.timeout)

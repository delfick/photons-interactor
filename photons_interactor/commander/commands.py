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
    """
    command = dictobj.Field(sb.string_spec, default="help"
        , help = "The command to show help for"
        )

    async def execute(self):
        if self.command not in available_commands:
            raise NoSuchCommand(wanted=self.command, available=sorted(available_commands))
        header = f"Command {self.command}"
        kls = available_commands[self.command]["kls"]
        doc = dedent(getattr(kls, "__help__", kls.__doc__))

        fields = chp.fields_description(kls)
        fields_string = ""
        if fields:
            fields_string = ["", "Arguments\n---------", ""]
            for name, type_info, desc in fields:
                fields_string.append(f"{name}: {type_info}")
                for line in desc.split("\n"):
                    fields_string.append(f"\t{line}")
                fields_string.append("")
            fields_string = "\n".join(fields_string)

        extra = ""
        if self.command == "help":
            extra = "\nAvailable commands:\n{}".format(
                  "\n".join(f" * {name}" for name in sorted(available_commands))
                )

        return f"{header}\n{'=' * len(header)}\n{doc}{fields_string}{extra}"

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

    multiple = dictobj.Field(sb.boolean, default=False
        , help = "Whether to expect multiple replies to our packet"
        )

    pkt_type = df.pkt_type_field
    pkt_args = df.pkt_args_field

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = chp.make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, timeout=self.timeout, multiple_replies=self.multiple)

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
            ``{"color": "blue", "effect": "breathe"}``
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

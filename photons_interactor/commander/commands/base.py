from photons_interactor.commander.errors import NoSuchCommand
from photons_interactor.commander.decorator import command
from photons_interactor.commander import helpers as chp

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

    @property
    def command_kls(self):
        if self.command not in command.available_commands:
            raise NoSuchCommand(wanted=self.command, available=sorted(command.available_commands))
        return command.available_commands[self.command]["kls"]

    async def execute(self):
        header = f"Command {self.command}"
        kls = self.command_kls
        doc = dedent(getattr(kls, "__help__", kls.__doc__))

        fields = chp.fields_description(kls)
        fields_string = ""
        if fields:
            fields_string = ["", "Arguments\n---------", ""]
            for name, type_info, desc in fields:
                fields_string.append(f"{name}: {type_info}")
                for line in desc.split("\n"):
                    if not line.strip():
                        fields_string.append("")
                    else:
                        fields_string.append(f"\t{line}")
                fields_string.append("")
            fields_string = "\n".join(fields_string)

        extra = ""
        if self.command == "help":
            extra = "\nAvailable commands:\n{}".format(
                  "\n".join(f" * {name}" for name in sorted(command.available_commands))
                )

        return f"{header}\n{'=' * len(header)}\n{doc}{fields_string}{extra}"

from photons_app.formatter import MergedOptionStringFormatter

from input_algorithms.errors import BadSpecValue
from input_algorithms import spec_base as sb

class command:
    """
    A decorator for registering a Command.

    We take in the name of the command as an argument and the kls and
    FieldSpec for that kls is registered in the available_commands
    dictionary under the specified name.
    """
    available_commands = {}

    def __init__(self, name):
        self.name = name

    def __call__(self, kls):
        kls.__interactor_command__ = True
        spec = kls.FieldSpec(formatter=MergedOptionStringFormatter)
        self.available_commands[self.name] = {"kls": kls, "spec": spec}
        return kls

class command_spec(sb.Spec):
    """
    Knows how to turn ``{"command": <string>, "args": <dict>}`` into a Command.

    It uses the FieldSpec in available_commands to normalise the args into
    the Command instance.
    """
    def normalise_filled(self, meta, val):
        val = sb.set_options(
              args = sb.dictionary_spec()
            , command = sb.required(sb.string_spec())
            ).normalise(meta, val)

        args = val["args"]
        name = val["command"]

        available_commands = command.available_commands

        if name not in available_commands:
            raise BadSpecValue("Unknown command", wanted=name, available=sorted(available_commands), meta=meta)

        return available_commands[name]["spec"].normalise(meta.at("args"), args)

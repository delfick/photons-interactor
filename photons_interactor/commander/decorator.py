from photons_app.formatter import MergedOptionStringFormatter

from input_algorithms.errors import BadSpecValue
from input_algorithms import spec_base as sb

available_commands = {}

class command:
    def __init__(self, name):
        self.name = name

    def __call__(self, kls):
        kls.__interactor_command__ = True
        spec = kls.FieldSpec(formatter=MergedOptionStringFormatter)
        available_commands[self.name] = {"kls": kls, "spec": spec}
        return kls

class command_spec(sb.Spec):
    def normalise_filled(self, meta, val):
        val = sb.set_options(
              args = sb.dictionary_spec()
            , command = sb.required(sb.string_spec())
            ).normalise(meta, val)

        args = val["args"]
        command = val["command"]

        if command not in available_commands:
            raise BadSpecValue("Unknown command", wanted=command, available=sorted(available_commands), meta=meta)

        return available_commands[command]["spec"].normalise(meta.at("args"), args)

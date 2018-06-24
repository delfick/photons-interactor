from photons_app.formatter import MergedOptionStringFormatter
from photons_app.errors import PhotonsAppError

from photons_transform.transformer import Transformer
from photons_device_finder import Filter

from input_algorithms.errors import BadSpecValue
from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from input_algorithms.meta import Meta
from option_merge import MergedOptions
from textwrap import dedent

available_commands = {}

class NoSuchCommand(PhotonsAppError):
    desc = "no such command"

class NoSuchPacket(PhotonsAppError):
    desc = "no such packet"

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

class Command(dictobj.Spec):
    async def execute(self):
        raise NotImplementedError("Base command has no execute implementation")

class Commander:
    def __init__(self, finder, target_register, protocol_register):
        self.command_spec = command_spec()

        self.meta = Meta(
              MergedOptions.using(
                { "finder": finder
                , "target_register": target_register
                , "protocol_register": protocol_register
                }
              )
            , []
            )

    async def execute(self, command):
        if not isinstance(command, Command):
            command = self.command_spec.normalise(self.meta.at("<input>"), command)
        return await command.execute()

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

finder_field = dictobj.Field(sb.overridden("{finder}"), formatted=True)
target_field = dictobj.Field(sb.overridden("{targets.lan}"), formatted=True)
refresh_field = dictobj.NullableField(sb.boolean)
timeout_field = dictobj.Field(sb.integer_spec, default=20)
matcher_field = dictobj.NullableField(sb.or_spec(sb.string_spec(), sb.dictionary_spec()))
protocol_register_field = dictobj.Field(sb.overridden("{protocol_register}"), formatted=True)

def filter_from_matcher(matcher, refresh=None):
    if matcher is None:
        fltr = Filter.empty()

    elif type(matcher) is str:
        fltr = Filter.from_key_value_str(matcher)

    else:
        fltr = Filter.from_options(matcher)

    if refresh is not None:
        fltr.force_refresh = refresh

    return fltr

def find_packet(protocol_register, pkt_type):
    for messages in protocol_register.message_register(1024):
        for typ, kls in messages.by_type.items():
            if typ == pkt_type or kls.__name__ == pkt_type:
                return kls

    raise NoSuchPacket(wanted=pkt_type)

def make_message(protocol_register, pkt_type, pkt_args):
    kls = find_packet(protocol_register, pkt_type)
    if pkt_args is not None:
        return kls.normalise(Meta.empty(), pkt_args)
    else:
        return kls()

async def run(script, fltr, finder, add_replies=True, **kwargs):
    result = ResultBuilder()

    afr = await finder.args_for_run()
    reference = await finder.serials(filtr=fltr)

    async for pkt, _, _ in script.run_with(reference, afr, error_catcher=result.error, **kwargs):
        if add_replies:
            result.add_packet(pkt)

    result = result.result

    for serial in reference:
        if serial not in result["results"]:
            result["results"][serial] = "ok"

    return result

class ResultBuilder:
    def __init__(self):
        self.result = {"results": {}}

    def add_packet(self, pkt):
        info = {
              "pkt_type": pkt.__class__.Payload.message_type
            , "pkt_name": pkt.__class__.__name__
            , "payload": {key: val for key, val in pkt.payload.as_dict().items() if "reserved" not in key}
            }

        if pkt.serial in self.result["results"]:
            existing = self.result["results"][pkt.serial]
            if type(existing) is list:
                existing.append(info)
            else:
                self.result["results"][pkt.serial] = [existing, info]
        else:
            self.result["results"][pkt.serial] = info

    def error(self, e):
        if hasattr(e, "as_dict"):
            err = e.as_dict()
        else:
            err = str(e)

        if hasattr(e, "kwargs") and "serial" in e.kwargs:
            self.result["results"][e.kwargs["serial"]] = {"error": err}
        else:
            if "errors" not in self.result:
                self.result["errors"] = []
            self.result["errors"].append(err)

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
    finder = finder_field
    matcher = matcher_field
    refresh = refresh_field
    just_serials = dictobj.Field(sb.boolean, default=False)

    async def execute(self):
        fltr = filter_from_matcher(self.matcher)

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
    finder = finder_field
    target = target_field
    matcher = matcher_field
    timeout = timeout_field
    refresh = refresh_field
    multiple = dictobj.Field(sb.boolean, default=False)
    protocol_register = protocol_register_field

    pkt_type = dictobj.Field(sb.or_spec(sb.integer_spec(), sb.string_spec()), wrapper=sb.required)
    pkt_args = dictobj.NullableField(sb.dictionary_spec())

    async def execute(self):
        fltr = filter_from_matcher(self.matcher, self.refresh)
        msg = make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        script = self.target.script(msg)
        return await run(script, fltr, self.finder, timeout=self.timeout, multiple_replies=self.multiple)

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
    finder = finder_field
    target = target_field
    matcher = matcher_field
    timeout = timeout_field
    refresh = refresh_field

    transform = dictobj.Field(sb.dictionary_spec(), wrapper=sb.required)

    async def execute(self):
        fltr = filter_from_matcher(self.matcher, self.refresh)
        msg = Transformer.using(self.transform)
        script = self.target.script(msg)
        return await run(script, fltr, self.finder, add_replies=False, timeout=self.timeout)

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
    finder = finder_field
    target = target_field
    matcher = matcher_field
    timeout = timeout_field
    refresh = refresh_field
    protocol_register = protocol_register_field

    pkt_type = dictobj.Field(sb.or_spec(sb.integer_spec(), sb.string_spec()), wrapper=sb.required)
    pkt_args = dictobj.NullableField(sb.dictionary_spec())

    async def execute(self):
        fltr = filter_from_matcher(self.matcher, self.refresh)
        msg = make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        msg.res_required = False
        script = self.target.script(msg)
        return await run(script, fltr, self.finder, timeout=self.timeout)

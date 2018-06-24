from photons_interactor.commander.spec_description import signature
from photons_interactor.commander.errors import NoSuchPacket

from photons_app.formatter import MergedOptionStringFormatter

from photons_device_finder import Filter

from input_algorithms.meta import Meta
from textwrap import dedent

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

    for serial in reference:
        result.set_ok(serial)

    return result

class ResultBuilder:
    def __init__(self):
        self.result = {"results": {}}

    def as_dict(self):
        return self.result

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

    def set_ok(self, serial):
        if serial not in self.result["results"]:
            self.result["results"][serial] = "ok"

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

def fields_description(kls):
    final_specs = kls.FieldSpec(formatter=MergedOptionStringFormatter).make_spec(Meta.empty()).kwargs

    for name, field in kls.fields.items():
        hlp = ""
        if type(field) is tuple:
            hlp, field = field
        else:
            hlp = field.help

        if hlp:
            yield name, " ".join(signature(final_specs[name])), dedent(hlp).strip()

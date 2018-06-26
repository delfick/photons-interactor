from photons_interactor.commander.spec_description import signature
from photons_interactor.commander.errors import NoSuchPacket

from photons_app.formatter import MergedOptionStringFormatter

from photons_device_finder import Filter

from input_algorithms.meta import Meta
from textwrap import dedent

def filter_from_matcher(matcher, refresh=None):
    """
    Return a Filter instance for our matcher

    If matcher is None, we return an empty Filter (catch all)

    If matcher is a string, we treat it as a key=value string

    If matcher is a dictionary, we pass in that as keyword arguments.

    If refresh is not None, then we set fltr.force_refresh as that value
    after we have created the filter
    """
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
    """
    Find the class that represents this pkt type.

    We assume protocol 1024 and can match pkt_type as the number for that packet
    or the name of the class photons gives that number.

    For example, ``find_packet(protocol_register, 117)`` is the same as
    ``find_packet(protocol_register, "SetPower")``
    """
    for messages in protocol_register.message_register(1024):
        for typ, kls in messages.by_type.items():
            if typ == pkt_type or kls.__name__ == pkt_type:
                return kls

    raise NoSuchPacket(wanted=pkt_type)

def make_message(protocol_register, pkt_type, pkt_args):
    """
    Find the packet class for this ``pkt_type`` and instantiate it with
    the provided ``pkt_args``.
    """
    kls = find_packet(protocol_register, pkt_type)
    if pkt_args is not None:
        return kls.normalise(Meta.empty(), pkt_args)
    else:
        return kls()

async def run(script, fltr, finder, add_replies=True, **kwargs):
    """
    Create a ResultBuilder, run the script with the serials found from this fltr
    and return the ResultBuilder after adding packets/errors/confirmation to it

    If add_replies is False then we won't add packets to the result builder

    Any extra kwargs will be given to ``run_with`` when we execute that on the script
    """
    afr = await finder.args_for_run()
    serials = await finder.serials(filtr=fltr)

    result = ResultBuilder(serials)

    async for pkt, _, _ in script.run_with(serials, afr, error_catcher=result.error, **kwargs):
        if add_replies:
            result.add_packet(pkt)

    return result

class ResultBuilder:
    """
    Responsible for creating a result to return.

    The result from calling as_dict on the ResultBuilder looks like::

        { "results":
          { <serial>:
            { "pkt_type": <integer>
            , "pkt_name": <string>
            , "payload": <dictionary>
            }
          , <serial>:
            [ { "pkt_type", "pkt_name", "payload" }
            , { "pkt_type", "pkt_name", "payload" }
            ]
          , <serial>: {"error": <error>}
          , <serial>: "ok"
          }
        , "errors":
          [ <error>
          , <error>
          ]
        }

    Where ``errors`` only appears if there were errors that can't be assigned to
    a particular serial.

    The result for each ``serial`` in ``results`` is a dictionary if there was only
    one reply for that serial, otherwise a list of replies.

    Each reply is displayed as the ``pkt_type``, ``pkt_name`` and ``payload`` from that
    reply.

    If there were no replies for a serial then we display ``"ok"`` for that serial.

    There are two methods on the result builder:

    add_packet(pkt)
        Takes in a new packet to put in the result.

    error(e)
        Record an error in the result
    """
    def __init__(self, serials):
        self.serials = serials
        self.result = {"results": {}}

    def as_dict(self):
        res = dict(self.result)
        res["results"] = dict(res["results"])
        for serial in self.serials:
            if serial not in res["results"]:
                res["results"][serial] = "ok"
        return res

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

def fields_description(kls):
    """
    yield (name, type_info, help) for all the fields on our kls

    Where type_info looks something like `integer (required)` or `string (default "blah")`

    and fields that have no help are skipped
    """
    final_specs = kls.FieldSpec(formatter=MergedOptionStringFormatter).make_spec(Meta.empty()).kwargs

    for name, field in kls.fields.items():
        hlp = ""
        if type(field) is tuple:
            hlp, field = field
        else:
            hlp = field.help

        if hlp:
            yield name, " ".join(signature(final_specs[name])), dedent(hlp).strip()

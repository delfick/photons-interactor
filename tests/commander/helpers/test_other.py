# coding: spec

from photons_interactor.commander.errors import NoSuchPacket
from photons_interactor.commander import helpers as chp

from photons_app.test_helpers import TestCase, AsyncTestCase
from photons_app.registers import ProtocolRegister
from photons_app.errors import PhotonsAppError

from photons_messages import DeviceMessages, LightMessages, LIFXPacket

from noseOfYeti.tokeniser.support import noy_sup_setUp
from input_algorithms import spec_base as sb
from unittest import mock
import asynctest

describe TestCase, "filter_from_matcher":
    def assertFilter(self, fltr, **kwargs):
        dct = {k: v for k, v in fltr.as_dict().items() if v is not sb.NotSpecified}
        self.assertEqual(dct, kwargs)

    it "returns empty filter if matcher is None":
        fltr = chp.filter_from_matcher(None)
        self.assertFilter(fltr, force_refresh=False)

        fltr = chp.filter_from_matcher(None, refresh=False)
        self.assertFilter(fltr, force_refresh=False)

        fltr = chp.filter_from_matcher(None, refresh=True)
        self.assertFilter(fltr, force_refresh=True)

    it "treats a string as a key value string":
        fltr = chp.filter_from_matcher("")
        self.assertFilter(fltr, force_refresh=False)

        fltr = chp.filter_from_matcher("label=one,two hue=20")
        self.assertFilter(fltr, force_refresh=False, label=["one", "two"], hue=[(20.0, 20.0)])

        fltr = chp.filter_from_matcher("label=one,two hue=20 force_refresh=true")
        self.assertFilter(fltr, force_refresh=True, label=["one", "two"], hue=[(20.0, 20.0)])

        fltr = chp.filter_from_matcher("label=one,two hue=20 force_refresh=true", refresh=False)
        self.assertFilter(fltr, force_refresh=False, label=["one", "two"], hue=[(20.0, 20.0)])

        fltr = chp.filter_from_matcher("label=one,two hue=20 force_refresh=false")
        self.assertFilter(fltr, force_refresh=False, label=["one", "two"], hue=[(20.0, 20.0)])

        fltr = chp.filter_from_matcher("label=one,two hue=20 force_refresh=false", refresh=True)
        self.assertFilter(fltr, force_refresh=True, label=["one", "two"], hue=[(20.0, 20.0)])

    it "treats a dictionary as a options":
        fltr = chp.filter_from_matcher({})
        self.assertFilter(fltr, force_refresh=False)

        fltr = chp.filter_from_matcher({"label": ["one", "two"], "hue": [(20, 20)]})
        self.assertFilter(fltr, force_refresh=False, label=["one", "two"], hue=[(20.0, 20.0)])

        fltr = chp.filter_from_matcher({"label": ["one", "two"], "hue": [(20, 20)], "force_refresh": True})
        self.assertFilter(fltr, force_refresh=True, label=["one", "two"], hue=[(20.0, 20.0)])

        fltr = chp.filter_from_matcher({"label": ["one", "two"], "hue": [(20, 20)], "force_refresh": True}, refresh=False)
        self.assertFilter(fltr, force_refresh=False, label=["one", "two"], hue=[(20.0, 20.0)])

        fltr = chp.filter_from_matcher({"label": ["one", "two"], "hue": [(20, 20)], "force_refresh": False})
        self.assertFilter(fltr, force_refresh=False, label=["one", "two"], hue=[(20.0, 20.0)])

        fltr = chp.filter_from_matcher({"label": ["one", "two"], "hue": [(20, 20)], "force_refresh": False}, refresh=True)
        self.assertFilter(fltr, force_refresh=True, label=["one", "two"], hue=[(20.0, 20.0)])

describe TestCase, "clone_filter":
    def assertFilter(self, fltr, **kwargs):
        dct = {k: v for k, v in fltr.as_dict().items() if v is not sb.NotSpecified}
        self.assertEqual(dct, kwargs)

    it "clones with additional kwargs":
        fltr = chp.filter_from_matcher({"label": ["one", "two"], "hue": [(20, 20)], "force_refresh": True}, refresh=True)
        self.assertFilter(fltr, force_refresh=True, label=["one", "two"], hue=[(20.0, 20.0)])
        self.assertFilter(chp.clone_filter(fltr, force_refresh=False), force_refresh=False, label=["one", "two"], hue=[(20.0, 20.0)])
        # Make sure the original isn't modified
        self.assertFilter(fltr, force_refresh=True, label=["one", "two"], hue=[(20.0, 20.0)])

        fltr = chp.filter_from_matcher({"label": "one", "hue": [(20, 20)], "force_refresh": True}, refresh=True)
        clone = chp.clone_filter(fltr, label=["three", "four"], location_name="blah")
        self.assertFilter(clone, force_refresh=True, label=["three", "four"], hue=[(20.0, 20.0)], location_name=["blah"])
        # Make sure the original isn't modified
        self.assertFilter(fltr, force_refresh=True, label=["one"], hue=[(20.0, 20.0)])

describe TestCase, "find_packet":
    before_each:
        self.protocol_register = ProtocolRegister()
        self.protocol_register.add(1024, LIFXPacket)
        self.protocol_register.message_register(1024).add(DeviceMessages)
        self.protocol_register.message_register(1024).add(LightMessages)

    it "can find a packet based on pkt_type integer":
        self.assertIs(chp.find_packet(self.protocol_register, 23), DeviceMessages.GetLabel)
        self.assertIs(chp.find_packet(self.protocol_register, 116), LightMessages.GetLightPower)

    it "can find a packet based on pkt_type name":
        self.assertIs(chp.find_packet(self.protocol_register, "GetLabel"), DeviceMessages.GetLabel)
        self.assertIs(chp.find_packet(self.protocol_register, "StatePower"), DeviceMessages.StatePower)

    it "complains if we can't find the packet":
        with self.fuzzyAssertRaisesError(NoSuchPacket, wanted="GetWat"):
            chp.find_packet(self.protocol_register, "GetWat")

        with self.fuzzyAssertRaisesError(NoSuchPacket, wanted=9001):
            chp.find_packet(self.protocol_register, 9001)

describe TestCase, "make_message":
    it "instantiates the kls without args if no pkt_args":
        pkt_type = mock.Mock(name="pkt_type")
        protocol_register = mock.Mock(name="protocol_register")

        find_packet = mock.Mock(name="find_packet", return_value=DeviceMessages.GetPower)
        with mock.patch("photons_interactor.commander.helpers.find_packet", find_packet):
            pkt = chp.make_message(protocol_register, pkt_type, {})

        assert isinstance(pkt, DeviceMessages.GetPower)
        find_packet.assert_called_once_with(protocol_register, pkt_type)

    it "instantiates the kls with args if have pkt_args":
        pkt_type = mock.Mock(name="pkt_type")
        protocol_register = mock.Mock(name="protocol_register")

        find_packet = mock.Mock(name="find_packet", return_value=LightMessages.SetLightPower)
        with mock.patch("photons_interactor.commander.helpers.find_packet", find_packet):
            pkt = chp.make_message(protocol_register, pkt_type, {"level": 65535, "duration": 10})

        assert isinstance(pkt, LightMessages.SetLightPower)
        self.assertEqual(pkt.payload.as_dict(), {"level": 65535, "duration": 10})
        find_packet.assert_called_once_with(protocol_register, pkt_type)

describe AsyncTestCase, "run":
    async it "builds a ResultBuilder":
        afr = mock.Mock(name="afr")
        serials = ["d073d5000001", "d073d5000002", "d073d5000003"]

        find = mock.Mock(name="find")
        finder = mock.Mock(name="finder")
        finder.serials = asynctest.mock.CoroutineMock(name="serials", return_value=serials)
        finder.args_for_run = asynctest.mock.CoroutineMock(name="args_for_run", return_value=afr)
        finder.find.return_value = find

        find_filter = mock.Mock(name="find_filtr")
        clone_filter = mock.Mock(name="clone_filter", return_value=find_filter)

        fltr = mock.Mock(name="fltr")
        fltr.as_dict.return_value = {}
        script = mock.Mock(name="script")

        run_with = mock.Mock(name="run_with")

        class RunWith:
            def __init__(self, *args, **kwargs):
                self.index = -1
                self.args = args
                self.kwargs = kwargs
                run_with(*args, **kwargs)

            def __aiter__(self):
                return self

            async def __anext__(self):
                self.index += 1
                if self.index == 0:
                    return (DeviceMessages.StatePower(level=0, target="d073d5000001"), ("192.168.0.1", 56700), "192.168.0.1")
                elif self.index == 1:
                    self.kwargs["error_catcher"](PhotonsAppError("failure", serial="d073d5000002"))
                    raise StopAsyncIteration
        script.run_with = RunWith

        with mock.patch("photons_interactor.commander.helpers.clone_filter", clone_filter):
            result = await self.wait_for(chp.run(script, fltr, finder, one=1))

        self.assertEqual(result.as_dict()
            , { "results":
                { "d073d5000001": {"pkt_type": 22, "pkt_name": "StatePower", "payload": {"level": 0}}
                , "d073d5000002": {"error": {"message": "failure"}, "error_code": "PhotonsAppError", "status": 400}
                , "d073d5000003": "ok"
                }
              }
            )

        finder.args_for_run.assert_called_once_with()
        finder.serials.assert_called_once_with(filtr=fltr)
        finder.find.assert_called_once_with(filtr=find_filter)
        clone_filter.assert_called_once_with(fltr, force_refresh=False)
        run_with.assert_called_once_with(find, afr, error_catcher=mock.ANY, one=1)

    async it "doesn't add packets if add_replies is False":
        afr = mock.Mock(name="afr")
        serials = ["d073d5000001", "d073d5000002", "d073d5000003"]

        find = mock.Mock(name="find")
        finder = mock.Mock(name="finder")
        finder.serials = asynctest.mock.CoroutineMock(name="serials", return_value=serials)
        finder.args_for_run = asynctest.mock.CoroutineMock(name="args_for_run", return_value=afr)
        finder.find.return_value = find

        find_filter = mock.Mock(name="find_filtr")
        clone_filter = mock.Mock(name="clone_filter", return_value=find_filter)

        fltr = mock.Mock(name="fltr")
        fltr.as_dict.return_value = {}
        script = mock.Mock(name="script")

        run_with = mock.Mock(name="run_with")

        class RunWith:
            def __init__(self, *args, **kwargs):
                self.index = -1
                self.args = args
                self.kwargs = kwargs
                run_with(*args, **kwargs)

            def __aiter__(self):
                return self

            async def __anext__(self):
                self.index += 1
                if self.index == 0:
                    return (DeviceMessages.StatePower(level=0, target="d073d5000001"), ("192.168.0.1", 56700), "192.168.0.1")
                elif self.index == 1:
                    return (DeviceMessages.StateHostFirmware(build=0, version=1.2, target="d073d5000002"), ("`92.168.0.2", 56700), "192.168.0.2")
                else:
                    raise StopAsyncIteration
        script.run_with = RunWith

        with mock.patch("photons_interactor.commander.helpers.clone_filter", clone_filter):
            result = await self.wait_for(chp.run(script, fltr, finder, add_replies=False, one=1))
        self.assertEqual(result.as_dict()
            , { "results":
                { "d073d5000001": "ok"
                , "d073d5000002": "ok"
                , "d073d5000003": "ok"
                }
              }
            )

        finder.args_for_run.assert_called_once_with()
        finder.serials.assert_called_once_with(filtr=fltr)
        finder.find.assert_called_once_with(filtr=find_filter)
        clone_filter.assert_called_once_with(fltr, force_refresh=False)
        run_with.assert_called_once_with(find, afr, error_catcher=mock.ANY, one=1)

# coding: spec

from photons_interactor.commander.store import store, load_commands
from photons_interactor.commander import test_helpers as cthp
from photons_interactor import test_helpers as thp

from photons_app.test_helpers import AsyncTestCase

from photons_messages import DeviceMessages
from photons_colour import Parser

import json

load_commands()
store = store.clone()

test_server = thp.ModuleLevelServer(store)

setUp = test_server.setUp
tearDown = test_server.tearDown

describe AsyncTestCase, "Control Commands":
    use_default_loop = True

    @test_server.test
    async it "has discovery commands", options, fake, server:
        await server.assertPUT(self, "/v1/lifx/command", {"command": "discover"}, json_output=cthp.discovery_response)

        res = await server.assertPUT(self, "/v1/lifx/command", {"command": "discover", "args": {"just_serials": True}})
        serials = json.loads(res.decode())
        self.assertEqual(sorted(serials), sorted(device.serial for device in fake.devices))

        res = await server.assertPUT(self, "/v1/lifx/command", {"command": "discover", "args": {"matcher": {"group_name": "Living Room"}}})
        j = json.loads(res.decode())
        wanted = {device.serial: cthp.discovery_response[device.serial]
              for device in fake.devices
              if device.group_label == "Living Room"
            }
        self.assertEqual(len(wanted), 2)
        self.assertEqual(j, wanted)

        res = await server.assertPUT(self, "/v1/lifx/command", {"command": "discover", "args": {"just_serials": True, "matcher": "label=kitchen"}})
        serials = json.loads(res.decode())
        self.assertEqual(serials, [fake.for_attribute("label", "kitchen")[0].serial])

        res = await server.assertPUT(self, "/v1/lifx/command", {"command": "discover", "args": {"just_serials": True, "matcher": "label=lamp"}})
        serials = json.loads(res.decode())
        self.assertEqual(serials, [d.serial for d in fake.for_attribute("label", "lamp", 2)])

        res = await server.assertPUT(self, "/v1/lifx/command", {"command": "discover", "args": {"just_serials": True, "matcher": "label=blah"}}, status=400)
        j = json.loads(res.decode())
        self.assertEqual(j, {"error": {"message": "Didn't find any devices"}, "status": 400, "error_code": "FoundNoDevices"})

    @test_server.test
    async it "has query commands", options, fake, server:
        await server.assertPUT(self, "/v1/lifx/command", {"command": "query", "args": {"pkt_type": 101}}, json_output=cthp.light_state_responses)

        results = cthp.light_state_responses["results"]
        expected = {device.serial: results[device.serial] for device in fake.for_attribute("power", 65535, expect=5)}
        await server.assertPUT(self, "/v1/lifx/command"
            , {"command": "query", "args": {"pkt_type": 101, "matcher": "power=on"}}
            , json_output = {"results": expected}
            )

        bathroom_light = fake.for_serial("d073d5000002")
        with bathroom_light.offline():
            expected["d073d5000002"] = {'error': {'message': 'Timed out. Waiting for reply to a packet'}, "error_code": "TimedOut", "status": 400}
            await server.assertPUT(self, "/v1/lifx/command"
                , {"command": "query", "args": {"pkt_type": 101, "matcher": "power=on", "timeout": 0.1}}
                , json_output = {"results": expected}
                )

        await server.assertPUT(self, "/v1/lifx/command", {"command": "query", "args": {"pkt_type": "GetLabel"}}
            , json_output=cthp.label_state_responses
            )

        await server.assertPUT(self, "/v1/lifx/command"
            , { "command": "query"
              , "args":
                { "pkt_type": 502
                , "pkt_args": {"start_index": 0, "end_index": 255}
                , "matcher": "cap=multizone"
                }
              }
            , json_output=cthp.multizone_state_responses
            )

    @test_server.test
    async it "has set commands", options, fake, server:
        expected = {"results": {device.serial: "ok" for device in fake.devices}}

        await server.assertPUT(self, "/v1/lifx/command", {"command": "set", "args": {"pkt_type": "SetPower", "pkt_args": {"level": 0}}}
            , json_output = expected
            )

        for device in fake.devices:
            device.expectSetMessages(DeviceMessages.SetPower(level=0, res_required=False))

        # With an offline light
        bathroom_light = fake.for_serial("d073d5000002")
        with bathroom_light.offline():
            expected["results"]["d073d5000002"] = {
                  'error': {'message': 'Timed out. Waiting for reply to a packet'}
                , "error_code": "TimedOut"
                , "status": 400
                }

            await server.assertPUT(self, "/v1/lifx/command"
                , {"command": "set", "args": {"pkt_type": "SetPower", "pkt_args": {"level": 65535}, "timeout": 0.1}}
                , json_output = expected
                )

            for device in fake.devices:
                if device is not bathroom_light:
                    device.expectSetMessages(DeviceMessages.SetPower(level=65535, res_required=False))

        # With a matcher
        kitchen_light = fake.for_attribute("label", "kitchen", expect=1)[0]
        expected = {"results": {kitchen_light.serial: "ok"}}

        await server.assertPUT(self, "/v1/lifx/command"
            , {"command": "set", "args": {"pkt_type": 24, "pkt_args": {"label": "blah"}, "matcher": "label=kitchen"}}
            , json_output = expected
            )

        kitchen_light.expectSetMessages(DeviceMessages.SetLabel(label="blah", res_required=False))
        for device in fake.devices:
            if device is not kitchen_light:
                device.expectNoSetMessages()

    @test_server.test
    async it "has transform command", options, fake, server:
        # Just power
        expected = {"results": {device.serial: "ok" for device in fake.devices}}

        await server.assertPUT(self, "/v1/lifx/command", {"command": "transform", "args": {"transform": {"power": "off"}}}
            , json_output = expected
            )

        for device in fake.devices:
            device.expectSetMessages(DeviceMessages.SetPower(level=0, res_required=False))

        # Just color
        await server.assertPUT(self, "/v1/lifx/command", {"command": "transform", "args": {"transform": {"color": "red", "effect": "sine"}}}
            , json_output = expected
            )

        for device in fake.devices:
            device.expectSetMessages(Parser.color_to_msg("red", overrides={"effect": "sine", "res_required": False}))

        # Power on and color
        for device in fake.devices:
            device.change_power(0)
            device.brightness = 0.5
        fake.for_serial("d073d5000001").change_power(65535)
        fake.for_serial("d073d5000003").change_power(65535)

        tv_light = fake.for_attribute("label", "tv", expect=1)[0]
        with tv_light.offline():
            expected["results"]["d073d5000006"] = {'error': {'message': 'Timed out. Waiting for reply to a packet'}, "error_code": "TimedOut", "status": 400}
            await server.assertPUT(self, "/v1/lifx/command"
                , {"command": "transform", "args": {"transform": {"power": "on", "color": "blue"}, "timeout": 0.2}}
                , json_output = expected
                )

        for device in fake.devices:
            if device.label == "tv":
                device.expectNoSetMessages()
            elif device.serial in ("d073d5000001", "d073d5000003"):
                device.expectSetMessages(
                      Parser.color_to_msg("blue", overrides={"res_required": False})
                    )
            else:
                device.expectSetMessages(
                      Parser.color_to_msg("blue", overrides={"brightness": 0, "res_required": False})
                    , DeviceMessages.SetPower(level=65535, res_required=False)
                    , Parser.color_to_msg("blue", overrides={"brightness": 0.5, "res_required": False})
                    )

# coding: spec

from photons_interactor.commander import test_helpers as cthp
from photons_interactor import test_helpers as thp

from photons_device_messages import DeviceMessages
from photons_colour import Parser

import json

describe thp.CommandCase, "Control Commands":
    async def assertDiscoverCommand(self, options, devices):
        await self.assertCommand(options, {"command": "discover"}, json_output=cthp.discovery_response)

        res = await self.assertCommand(options, {"command": "discover", "args": {"just_serials": True}})
        serials = json.loads(res.decode())
        self.assertEqual(sorted(serials), sorted(device.serial for device in devices["devices"]))

        res = await self.assertCommand(options, {"command": "discover", "args": {"matcher": {"group_name": "Living Room"}}})
        j = json.loads(res.decode())
        wanted = {device.serial: cthp.discovery_response[device.serial]
              for device in devices["devices"]
              if device.group_label == "Living Room"
            }
        self.assertEqual(len(wanted), 2)
        self.assertEqual(j, wanted)

        res = await self.assertCommand(options, {"command": "discover", "args": {"just_serials": True, "matcher": "label=kitchen"}})
        serials = json.loads(res.decode())
        self.assertEqual(serials, [devices["devices"][0].serial])

        res = await self.assertCommand(options, {"command": "discover", "args": {"just_serials": True, "matcher": "label=lamp"}})
        serials = json.loads(res.decode())
        self.assertEqual(serials, [devices["devices"][2].serial, devices["devices"][3].serial])

        res = await self.assertCommand(options, {"command": "discover", "args": {"just_serials": True, "matcher": "label=blah"}}, status=400)
        j = json.loads(res.decode())
        self.assertEqual(j, {"error": {"message": "Didn't find any devices"}, "status": 400, "error_code": "FoundNoDevices"})

    async def assertQueryCommand(self, options, devices):
        await self.assertCommand(options, {"command": "query", "args": {"pkt_type": 101}}, json_output=cthp.light_state_responses)

        results = cthp.light_state_responses["results"]
        expected = {device.serial: results[device.serial] for device in devices["devices"] if device.power == 65535}
        self.assertEqual(len(expected), 5)
        await self.assertCommand(options
            , {"command": "query", "args": {"pkt_type": 101, "matcher": "power=on"}}
            , json_output = {"results": expected}
            )

        bathroom_light = devices["devices"][1]
        with bathroom_light.offline():
            expected["d073d5000002"] = {'error': {'message': 'Timed out. Waiting for reply to a packet'}, "error_code": "TimedOut", "status": 400}
            await self.assertCommand(options
                , {"command": "query", "args": {"pkt_type": 101, "matcher": "power=on", "timeout": 0.1}}
                , json_output = {"results": expected}
                )

        await self.assertCommand(options, {"command": "query", "args": {"pkt_type": "GetLabel"}}
            , json_output=cthp.label_state_responses
            )

        await self.assertCommand(options
            , { "command": "query"
              , "args":
                { "pkt_type": 502
                , "pkt_args": {"start_index": 0, "end_index": 255}
                , "matcher": "cap=multizone"
                }
              }
            , json_output=cthp.multizone_state_responses
            )

    async def assertSetCommand(self, options, devices):
        expected = {"results": {device.serial: "ok" for device in devices["devices"]}}

        await self.assertCommand(options, {"command": "set", "args": {"pkt_type": "SetPower", "pkt_args": {"level": 0}}}
            , json_output = expected
            )

        for device in devices["devices"]:
            device.expectSetMessages(DeviceMessages.SetPower(level=0, res_required=False))

        # With an offline light
        bathroom_light = devices["devices"][1]
        with bathroom_light.offline():
            expected["results"]["d073d5000002"] = {
                  'error': {'message': 'Timed out. Waiting for reply to a packet'}
                , "error_code": "TimedOut"
                , "status": 400
                }

            await self.assertCommand(options
                , {"command": "set", "args": {"pkt_type": "SetPower", "pkt_args": {"level": 65535}, "timeout": 0.1}}
                , json_output = expected
                )

            for device in devices["devices"]:
                if device is not bathroom_light:
                    device.expectSetMessages(DeviceMessages.SetPower(level=65535, res_required=False))

        # With a matcher
        kitchen_light = devices["devices"][0]
        self.assertEqual(kitchen_light.label, "kitchen")
        expected = {"results": {kitchen_light.serial: "ok"}}

        await self.assertCommand(options
            , {"command": "set", "args": {"pkt_type": 24, "pkt_args": {"label": "blah"}, "matcher": "label=kitchen"}}
            , json_output = expected
            )

        kitchen_light.expectSetMessages(DeviceMessages.SetLabel(label="blah", res_required=False))
        for device in devices["devices"]:
            if device is not kitchen_light:
                device.expectNoSetMessages()

    async def assertTransformCommand(self, options, devices):
        # Just power
        expected = {"results": {device.serial: "ok" for device in devices["devices"]}}

        await self.assertCommand(options, {"command": "transform", "args": {"transform": {"power": "off"}}}
            , json_output = expected
            )

        for device in devices["devices"]:
            device.expectSetMessages(DeviceMessages.SetPower(level=0, res_required=False))

        # Just color
        await self.assertCommand(options, {"command": "transform", "args": {"transform": {"color": "red", "effect": "sine"}}}
            , json_output = expected
            )

        for device in devices["devices"]:
            device.expectSetMessages(Parser.color_to_msg("red", overrides={"effect": "sine", "res_required": False}))

        # Power on and color
        for device in devices["devices"]:
            device.change_power(0)
            device.brightness = 0.5
        devices["devices"][0].change_power(65535)
        devices["devices"][2].change_power(65535)

        tv_light = devices["devices"][5]
        self.assertEqual(tv_light.label, "tv")
        with tv_light.offline():
            expected["results"]["d073d5000006"] = {'error': {'message': 'Timed out. Waiting for reply to a packet'}, "error_code": "TimedOut", "status": 400}
            await self.assertCommand(options
                , {"command": "transform", "args": {"transform": {"power": "on", "color": "blue"}, "timeout": 0.2}}
                , json_output = expected
                )

        for i, device in enumerate(devices["devices"]):
            if i == 5:
                device.expectNoSetMessages()
            elif i in (0, 2):
                device.expectSetMessages(
                      Parser.color_to_msg("blue", overrides={"res_required": False})
                    )
            else:
                device.expectSetMessages(
                      Parser.color_to_msg("blue", overrides={"brightness": 0, "res_required": False})
                    , DeviceMessages.SetPower(level=65535, res_required=False)
                    , Parser.color_to_msg("blue", overrides={"brightness": 0.5, "res_required": False})
                    )

    async it "has control commands":
        async def runner(options, fake, server):
            for test in ("Discover", "Query", "Set", "Transform"):
                for device in fake["devices"]:
                    device.reset()
                await getattr(self, f"assert{test}Command")(options, fake)

        await self.wait_for(self.run_server(None, runner), timeout=8)

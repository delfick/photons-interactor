# coding: spec

from photons_interactor.commander.store import store, load_commands
from photons_interactor.commander import test_helpers as cthp

from photons_messages import DeviceMessages
from photons_colour import Parser

import pytest
import json


@pytest.fixture(scope="module")
def store_clone():
    load_commands()
    return store.clone()


@pytest.fixture(scope="module")
async def wrapper(store_clone, server_wrapper):
    async with server_wrapper(store_clone) as wrapper:
        yield wrapper


@pytest.fixture(autouse=True)
async def wrap_tests(wrapper):
    async with wrapper.test_wrap():
        yield


@pytest.fixture()
def runner(wrapper):
    return wrapper.runner


describe "Control Commands":
    async it "has discovery commands", fake, runner, asserter:
        await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "discover"},
            json_output=cthp.discovery_response,
        )

        res = await runner.assertPUT(
            asserter, "/v1/lifx/command", {"command": "discover", "args": {"just_serials": True}}
        )
        serials = json.loads(res.decode())
        assert sorted(serials) == sorted(device.serial for device in fake.devices)

        res = await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "discover", "args": {"matcher": {"group_name": "Living Room"}}},
        )
        j = json.loads(res.decode())
        wanted = {
            device.serial: cthp.discovery_response[device.serial]
            for device in fake.devices
            if device.attrs.group.label == "Living Room"
        }
        assert len(wanted) == 2
        assert j == wanted

        res = await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "discover", "args": {"just_serials": True, "matcher": "label=kitchen"}},
        )
        serials = json.loads(res.decode())
        assert serials == [fake.for_attribute("label", "kitchen")[0].serial]

        res = await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "discover", "args": {"just_serials": True, "matcher": "label=lamp"}},
        )
        serials = json.loads(res.decode())
        assert serials == [d.serial for d in fake.for_attribute("label", "lamp", 2)]

        res = await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "discover", "args": {"just_serials": True, "matcher": "label=blah"}},
            status=400,
        )
        j = json.loads(res.decode())
        assert j == {
            "error": {"message": "Didn't find any devices"},
            "status": 400,
            "error_code": "FoundNoDevices",
        }

    async it "has query commands", fake, runner, asserter:
        await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "query", "args": {"pkt_type": 101}},
            json_output=cthp.light_state_responses,
        )

        results = cthp.light_state_responses["results"]
        expected = {
            device.serial: results[device.serial]
            for device in fake.for_attribute("power", 65535, expect=5)
        }
        await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "query", "args": {"pkt_type": 101, "matcher": "power=on"}},
            json_output={"results": expected},
        )

        bathroom_light = fake.for_serial("d073d5000002")
        with bathroom_light.offline():
            expected["d073d5000002"] = {
                "error": {"message": "Timed out. Waiting for reply to a packet"},
                "error_code": "TimedOut",
                "status": 400,
            }
            await runner.assertPUT(
                asserter,
                "/v1/lifx/command",
                {
                    "command": "query",
                    "args": {"pkt_type": 101, "matcher": "power=on", "timeout": 0.1},
                },
                json_output={"results": expected},
            )

        await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "query", "args": {"pkt_type": "GetLabel"}},
            json_output=cthp.label_state_responses,
        )

        await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {
                "command": "query",
                "args": {
                    "pkt_type": 502,
                    "pkt_args": {"start_index": 0, "end_index": 255},
                    "matcher": "cap=multizone",
                },
            },
            json_output=cthp.multizone_state_responses,
        )

    async it "has set commands", fake, runner, asserter:
        expected = {"results": {device.serial: "ok" for device in fake.devices}}

        await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "set", "args": {"pkt_type": "SetPower", "pkt_args": {"level": 0}}},
            json_output=expected,
        )

        for device in fake.devices:
            device.compare_received_set([DeviceMessages.SetPower(level=0)])
            device.reset_received()

        # With an offline light
        bathroom_light = fake.for_serial("d073d5000002")
        with bathroom_light.offline():
            expected["results"]["d073d5000002"] = {
                "error": {"message": "Timed out. Waiting for reply to a packet"},
                "error_code": "TimedOut",
                "status": 400,
            }

            await runner.assertPUT(
                asserter,
                "/v1/lifx/command",
                {
                    "command": "set",
                    "args": {"pkt_type": "SetPower", "pkt_args": {"level": 65535}, "timeout": 0.1},
                },
                json_output=expected,
            )

            for device in fake.devices:
                if device is not bathroom_light:
                    device.compare_received_set([DeviceMessages.SetPower(level=65535)])
                    device.reset_received()

        # With a matcher
        kitchen_light = fake.for_attribute("label", "kitchen", expect=1)[0]
        expected = {"results": {kitchen_light.serial: "ok"}}

        await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {
                "command": "set",
                "args": {"pkt_type": 24, "pkt_args": {"label": "blah"}, "matcher": "label=kitchen"},
            },
            json_output=expected,
        )

        kitchen_light.compare_received_set([DeviceMessages.SetLabel(label="blah")])
        for device in fake.devices:
            if device is not kitchen_light:
                device.expect_no_set_messages()

    async it "has transform command", fake, runner, asserter:
        # Just power
        expected = {"results": {device.serial: "ok" for device in fake.devices}}

        await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "transform", "args": {"transform": {"power": "off"}}},
            json_output=expected,
        )

        for device in fake.devices:
            device.compare_received_set([DeviceMessages.SetPower(level=0)])
            device.reset_received()

        # Just color
        await runner.assertPUT(
            asserter,
            "/v1/lifx/command",
            {"command": "transform", "args": {"transform": {"color": "red", "effect": "sine"}}},
            json_output=expected,
        )

        for device in fake.devices:
            device.compare_received_set(
                [Parser.color_to_msg("red", overrides={"effect": "sine", "res_required": False})]
            )
            device.reset_received()

        # Power on and color
        for device in fake.devices:
            device.attrs.power = 0
            device.attrs.color.brightness = 0.5
        fake.for_serial("d073d5000001").attrs.power = 65535
        fake.for_serial("d073d5000003").attrs.power = 65535

        tv_light = fake.for_attribute("label", "tv", expect=1)[0]
        with tv_light.offline():
            expected["results"]["d073d5000006"] = {
                "error": {"message": "Timed out. Waiting for reply to a packet"},
                "error_code": "TimedOut",
                "status": 400,
            }
            await runner.assertPUT(
                asserter,
                "/v1/lifx/command",
                {
                    "command": "transform",
                    "args": {"transform": {"power": "on", "color": "blue"}, "timeout": 0.2},
                },
                json_output=expected,
            )

        for device in fake.devices:
            if device.attrs.label == "tv":
                device.expect_no_set_messages()
            elif device.serial in ("d073d5000001", "d073d5000003"):
                device.compare_received_set(
                    [Parser.color_to_msg("blue", overrides={"res_required": False})]
                )
            else:
                device.compare_received_set(
                    [
                        Parser.color_to_msg(
                            "blue", overrides={"brightness": 0, "res_required": False}
                        ),
                        DeviceMessages.SetPower(level=65535, res_required=False),
                        Parser.color_to_msg(
                            "blue", overrides={"brightness": 0.5, "res_required": False}
                        ),
                    ]
                )

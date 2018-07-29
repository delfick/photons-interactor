# coding: spec

from photons_interactor.commander import test_helpers as cthp
from photons_interactor.commander.decorator import command
from photons_interactor.commander.commands import Command
from photons_interactor import test_helpers as thp
from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_device_messages import DeviceMessages
from photons_colour import Parser

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from contextlib import contextmanager
from textwrap import dedent
from unittest import mock
import http.client
import asyncio
import json
import uuid

class TestCommand(Command):
    """
    A test command to test help output
    """
    one = dictobj.Field(sb.integer_spec, default=20
        , help = """
            one is the first number

            it is the best number
          """
        )

    two = dictobj.Field(sb.string_spec, wrapper=sb.required
        , help = "two is the second best number"
        )

    three = dictobj.Field(sb.boolean, default=True)

    async def execute(self):
        return self.as_dict()

describe thp.CommandCase, "Commands":
    async def assertHelpCommand(self, options, devices):
        want = dedent("""
        Command test
        ============

        A test command to test help output

        Arguments
        ---------

        one: integer (default 20)
        \tone is the first number

        \tit is the best number

        two: string (required)
        \ttwo is the second best number
        """).lstrip()

        await self.assertCommand(options, {"command": "help", "args": {"command": "test"}}, text_output=want.encode())

    async def assertTestCommand(self, options, devices):
        await self.assertCommand(options, {"command": "test"}, status=400
            , json_output = {
                  'error':
                  { 'errors': [{'message': 'Bad value. Expected a value but got none', 'meta': '{path=<input>.args.two}'}]
                  , 'message': 'Bad value'
                  , 'meta': '{path=<input>.args}'
                  }
                , "error_code": "BadSpecValue"
                , 'status': 400
                }
            )

        await self.assertCommand(options, {"command": "test", "args": {"one": 1, "two": "TWO", "three": True}}
            , json_output = {"one": 1, "two": "TWO", "three": True}
            )

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
            expected["d073d5000002"] = {'error': {'message': 'Timed out. Waiting for reply to a packet'}, "error_code": "TimedOut"}
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
                , "multiple": True
                }
              }
            , json_output=cthp.multizone_state_responses
            )

        # and without multiple
        results = {}
        for serial, payloads in cthp.multizone_state_responses["results"].items():
            results[serial] = payloads[0]

        await self.assertCommand(options
            , { "command": "query"
              , "args":
                { "pkt_type": 502
                , "pkt_args": {"start_index": 0, "end_index": 255}
                , "matcher": "cap=multizone"
                , "multiple": False
                }
              }
            , json_output = {'results': results}
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
            expected["results"]["d073d5000006"] = {'error': {'message': 'Timed out. Waiting for reply to a packet'}, "error_code": "TimedOut"}
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

    async def assertWS(self, options, devices, server):
        connection = await server.ws_connect()

        # Invalid path
        msg_id = str(uuid.uuid1())
        await server.ws_write(connection
            , {"path": "/blah", "body": {"stuff": True}, "message_id": msg_id}
            )

        error = "Specified path is invalid: /blah"
        self.assertEqual(await server.ws_read(connection)
            , {"message_id": msg_id, "reply": {"error": error, "status": 404}}
            )

        # invalid command
        msg_id = str(uuid.uuid1())
        await server.ws_write(connection
            , {"path": "/v1/lifx/command", "body": {"command": "nope"}, "message_id": msg_id}
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply":
                { "error":
                  { "message": 'Bad value. Unknown command'
                  , "wanted": "nope"
                  , "meta": '{path=<input>}'
                  , "available":
                    [ "discover"
                    , "help"
                    , "query"
                    , "scene_apply"
                    , "scene_capture"
                    , "scene_change"
                    , "scene_delete"
                    , "scene_info"
                    , "set"
                    , "test"
                    , "transform"
                    ]
                  }
                , "error_code": "BadSpecValue"
                , "status": 400
                }
              }
            )

        # valid command
        msg_id = str(uuid.uuid1())
        args = {"one": 1, "two": "TWO", "three": True}
        await server.ws_write(connection
            , {"path": "/v1/lifx/command", "body": {"command": "test", "args": args}, "message_id": msg_id}
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply": {"one": 1, "two": "TWO", "three": True}
              }
            )

        # another valid command
        msg_id = str(uuid.uuid1())
        args = {"one": 1, "two": "TWO", "three": True}
        await server.ws_write(connection
            , {"path": "/v1/lifx/command", "body": {"command": "query", "args": {"pkt_type": 101}}, "message_id": msg_id}
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply": cthp.light_state_responses
              }
            )

        connection.close()
        self.assertIs(await server.ws_read(connection), None)

    async it "works":
        @contextmanager
        def wrapper():
            try:
                command(name="test")(TestCommand)
                yield
            finally:
                if "test" in command.available_commands:
                    del command.available_commands["test"]

        async def runner(options, fake, server):
            for test in ("Help", "Test", "Discover", "Query", "Set", "Transform"):
                for device in fake["devices"]:
                    device.reset()
                await getattr(self, f"assert{test}Command")(options, fake)

            for device in fake["devices"]:
                device.reset()
            await self.assertWS(options, fake, server)

        await self.wait_for(self.run_server(wrapper, runner), timeout=6)

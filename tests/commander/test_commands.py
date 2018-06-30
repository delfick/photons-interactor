# coding: spec

from photons_interactor.commander import test_helpers as cthp
from photons_interactor.commander.decorator import command
from photons_interactor.commander.commands import Command
from photons_interactor import test_helpers as thp
from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_app.test_helpers import AsyncTestCase

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from contextlib import contextmanager
from textwrap import dedent
from unittest import mock
import http.client
import asyncio
import json

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

describe AsyncTestCase, "Commands":
    async def assertCommand(self, options, command, status=200, json_output=None, text_output=None, timeout=None):
        def doit():
            conn = http.client.HTTPConnection("127.0.0.1", options.port, timeout=timeout)
            conn.request("PUT", "/v1/lifx/command", body=json.dumps(command).encode())
            res = conn.getresponse()

            body = res.read()

            self.assertEqual(res.status, status, body)
            if json_output is None and text_output is None:
                return body
            else:
                if json_output:
                    self.maxDiff = None
                    self.assertEqual(json.loads(body.decode()), json_output)
                else:
                    self.assertEqual(body, text_output)
        return await self.wait_for(self.loop.run_in_executor(None, doit), timeout=timeout)

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

    async it "works":
        final_future = asyncio.Future()

        options = Options.FieldSpec().empty_normalise(
              host = "127.0.0.1"
            , port = thp.free_port()
            , device_finder_repeat_spread = 0.01
            )

        protocol_register = cthp.make_protocol_register()
        lan_target = cthp.make_memory_target(final_future)

        target_register = mock.Mock(name="target_register")
        target_register.resolve.return_value = lan_target

        fake = cthp.fake_devices(protocol_register)

        cleaners = []
        server = Server(final_future, options, cleaners, target_register, protocol_register)

        async def doit():
            @contextmanager
            def wrapper():
                try:
                    command(name="test")(TestCommand)
                    yield
                finally:
                    if "test" in command.available_commands:
                        del command.available_commands["test"]

            async with cthp.MemoryTargetRunner(lan_target, fake["devices"]):
                async with thp.ServerRunner(final_future, server, options, wrapper()):
                    await self.assertHelpCommand(options, fake)
                    await self.assertTestCommand(options, fake)
                    await self.assertDiscoverCommand(options, fake)

        await self.wait_for(doit(), timeout=6)

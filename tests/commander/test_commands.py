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
    async def assertCommand(self, options, command, json_output=None, text_output=None):
        if json_output is None and text_output is None:
            assert False, "Must specify json_output or text_output"

        def doit():
            conn = http.client.HTTPConnection("127.0.0.1", options.port, timeout=5)
            conn.request("PUT", "/v1/lifx/command", body=json.dumps(command).encode())
            res = conn.getresponse()

            self.assertEqual(res.status, 200)
            if json_output:
                self.assertEqual(json.loads(res.read().decode()), json_output)
            else:
                self.assertEqual(res.read(), text_output)
        await self.wait_for(self.loop.run_in_executor(None, doit))

    async def assertHelpCommand(self, options):
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

    async it "works":
        final_future = asyncio.Future()

        options = Options.FieldSpec().empty_normalise(
              host = "127.0.0.1"
            , port = thp.free_port()
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
                    await self.assertHelpCommand(options)

        await self.wait_for(doit(), timeout=6)

# coding: spec

from photons_interactor.commander import test_helpers as cthp
from photons_interactor.commander.decorator import command
from photons_interactor.commander.commands import Command
from photons_interactor import test_helpers as thp

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from contextlib import contextmanager
from textwrap import dedent
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

        reply = await server.ws_read(connection)

        assert "test" in reply["reply"]["error"]["available"]
        reply["reply"]["error"]["available"] = ["test"]

        self.assertEqual(reply
            , { "message_id": msg_id
              , "reply":
                { "error":
                  { "message": 'Bad value. Unknown command'
                  , "wanted": "nope"
                  , "meta": '{path=<input>}'
                  , "available":
                    [ "test"
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

    @contextmanager
    def register_test_command(self):
        try:
            command(name="test")(TestCommand)
            yield
        finally:
            if "test" in command.available_commands:
                del command.available_commands["test"]

    async it "has base commands":
        async def runner(options, fake, server):
            for test in ("Help", "Test"):
                for device in fake["devices"]:
                    device.reset()
                await getattr(self, f"assert{test}Command")(options, fake)

        await self.wait_for(self.run_server(self.register_test_command(), runner))

    async it "has websocket commands":
        async def runner(options, fake, server):
            await self.assertWS(options, fake, server)

        await self.wait_for(self.run_server(self.register_test_command(), runner), timeout=6)

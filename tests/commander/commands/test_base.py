# coding: spec

from photons_interactor.commander.store import store, load_commands
from photons_interactor.commander import test_helpers as cthp
from photons_interactor import test_helpers as thp

from photons_app.test_helpers import AsyncTestCase

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from textwrap import dedent
from unittest import mock

load_commands()
store = store.clone()

@store.command("test")
class TestCommand(store.Command):
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

test_server = thp.ModuleLevelServer(store)

setUp = test_server.setUp
tearDown = test_server.tearDown

describe AsyncTestCase, "commands":
    use_default_loop = True

    @test_server.test
    async it "has a help command", options, fake, server:
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

        await server.assertPUT(self, "/v1/lifx/command", {"command": "help", "args": {"command": "test"}}, text_output=want.encode())

    @test_server.test
    async it "has a test command", options, fake, server:
        await server.assertPUT(self, "/v1/lifx/command", {"command": "test"}
            , status=400
            , json_output = {
                  'error':
                  { 'errors': [{'message': 'Bad value. Expected a value but got none', 'meta': '{path=<input>.body.args.two}'}]
                  , 'message': 'Bad value'
                  , 'meta': '{path=<input>.body.args}'
                  }
                , "error_code": "BadSpecValue"
                , 'status': 400
                }
            )

        await server.assertPUT(self, "/v1/lifx/command", {"command": "test", "args": {"one": 1, "two": "TWO", "three": True}}
            , json_output = {"one": 1, "two": "TWO", "three": True}
            )

    @test_server.test
    async it "has websocket commands", options, fake, server:
        async with server.ws_stream(self) as stream:
            # Invalid path
            await stream.start("/blah", {"stuff": True})
            error = "Specified path is invalid"
            await stream.check_reply({"error": error, "wanted": "/blah", "available": ["/v1/lifx/command"], "status": 404})

            # invalid command
            await stream.start("/v1/lifx/command", {"command": "nope"})
            reply = await stream.check_reply(mock.ANY)
            assert "test" in reply["error"]["available"]
            reply["error"]["available"] = ["test"]

            self.assertEqual(reply
                , { "error":
                    { "message": 'Bad value. Unknown command'
                    , "wanted": "nope"
                    , "meta": '{path=<input>.body.command}'
                    , "available":
                      [ "test"
                      ]
                    }
                  , "error_code": "BadSpecValue"
                  , "status": 400
                  }
                )

            # valid command
            args = {"one": 1, "two": "TWO", "three": True}
            await stream.start("/v1/lifx/command", {"command": "test", "args": args})
            await stream.check_reply(args)

            # another valid command
            await stream.start("/v1/lifx/command", {"command": "query", "args": {"pkt_type": 101}})
            await stream.check_reply(cthp.light_state_responses)

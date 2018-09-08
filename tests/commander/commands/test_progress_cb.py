# coding: spec

from photons_interactor.commander import default_fields as df
from photons_interactor.commander.decorator import command
from photons_interactor.commander.commands import Command
from photons_interactor.errors import InteractorError
from photons_interactor import test_helpers as thp

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from contextlib import contextmanager
import random
import uuid

serial_field = dictobj.Field(sb.string_spec, wrapper=sb.required)

class TestDoneProgress(Command):
    serial = serial_field
    progress_cb = df.progress_cb_field

    async def execute(self):
        self.progress_cb(None, serial=self.serial)
        return {"serial": self.serial}

class TestNoError(Command):
    serial = serial_field
    progress_cb = df.progress_cb_field

    async def execute(self):
        self.progress_cb("hello", serial=self.serial)
        self.progress_cb("there")
        return {"serial": self.serial}

class TestError(Command):
    serial = serial_field
    progress_cb = df.progress_cb_field

    async def execute(self):
        self.progress_cb(Exception("Nope"), serial=self.serial)
        self.progress_cb(ValueError("Yeap"))

        class Problem(InteractorError):
            desc = "a problem"
        self.progress_cb(Problem("wat", one=1), serial=self.serial)
        return {"serial": self.serial}

describe thp.CommandCase, "Commands":
    def command(self, command):
        serial = "d073d5{:06d}".format(random.randrange(1, 9999))
        cmd = {"command": command, "args": {"serial": serial}}
        return cmd, serial

    async def assertHTTP(self, options):
        command, serial = self.command("test_no_error")
        await self.assertCommand(options, command, status=200
            , json_output = {"serial": serial}
            )

        command, serial = self.command("test_error")
        await self.assertCommand(options, command, status=200
            , json_output = {"serial": serial}
            )

        command, serial = self.command("test_done_progress")
        await self.assertCommand(options, command, status=200
            , json_output = {"serial": serial}
            )

    async def assertWS(self, options, server):
        connection = await server.ws_connect()

        # Done progress
        command, serial = self.command("test_done_progress")
        msg_id = str(uuid.uuid1())
        await server.ws_write(connection
            , {"path": "/v1/lifx/command", "body": command, "message_id": msg_id}
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply": {"progress": {"done": True, "serial": serial}}
              }
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply": {"serial": serial}
              }
            )

        # No error
        command, serial = self.command("test_no_error")
        msg_id = str(uuid.uuid1())
        await server.ws_write(connection
            , {"path": "/v1/lifx/command", "body": command, "message_id": msg_id}
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply": {"progress": {"info": "hello", "serial": serial}}
              }
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply": {"progress": {"info": "there"}}
              }
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply": {"serial": serial}
              }
            )

        # With error
        command, serial = self.command("test_error")
        msg_id = str(uuid.uuid1())
        await server.ws_write(connection
            , {"path": "/v1/lifx/command", "body": command, "message_id": msg_id}
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply": {"progress": {"error": "Nope", "error_code": "Exception", "serial": serial}}
              }
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply": {"progress": {"error": "Yeap", "error_code": "ValueError"}}
              }
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply":
                { "progress":
                  { "error": {"message": "a problem. wat", "one": 1}
                  , "error_code": "Problem"
                  , "serial": serial
                  }
                }
              }
            )

        self.assertEqual(await server.ws_read(connection)
            , { "message_id": msg_id
              , "reply": {"serial": serial}
              }
            )

        connection.close()
        self.assertIs(await server.ws_read(connection), None)

    @contextmanager
    def register_test_commands(self):
        try:
            command(name="test_error")(TestError)
            command(name="test_no_error")(TestNoError)
            command(name="test_done_progress")(TestDoneProgress)
            yield
        finally:
            for attr in ('test_error', 'test_no_error'):
                if attr in command.available_commands:
                    del command.available_commands[attr]

    async it "has progress cb functionality":
        async def runner(options, fake, server):
            await self.assertHTTP(options)
            await self.assertWS(options, server)

        await self.wait_for(self.run_server(self.register_test_commands(), runner), timeout=6)

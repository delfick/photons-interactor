# coding: spec

from photons_interactor.commander import default_fields as df
from photons_interactor.errors import InteractorError
from photons_interactor import test_helpers as thp

from photons_app.formatter import MergedOptionStringFormatter
from photons_app.test_helpers import AsyncTestCase

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from contextlib import contextmanager
from whirlwind.store import Store
import random
import uuid

store = Store(default_path="/v1/lifx/command", formatter=MergedOptionStringFormatter)

serial_field = dictobj.Field(sb.string_spec, wrapper=sb.required)


@store.command("test_done_progress")
class TestDoneProgress(store.Command):
    serial = serial_field
    progress_cb = store.injected("progress_cb")

    async def execute(self):
        self.progress_cb(None, serial=self.serial)
        return {"serial": self.serial}


@store.command("test_no_error")
class TestNoError(store.Command):
    serial = serial_field
    progress_cb = store.injected("progress_cb")

    async def execute(self):
        self.progress_cb("hello", serial=self.serial)
        self.progress_cb("there")
        return {"serial": self.serial}


@store.command("test_error")
class TestError(store.Command):
    serial = serial_field
    progress_cb = store.injected("progress_cb")

    async def execute(self):
        self.progress_cb(Exception("Nope"), serial=self.serial)
        self.progress_cb(ValueError("Yeap"))

        class Problem(InteractorError):
            desc = "a problem"

        self.progress_cb(Problem("wat", one=1), serial=self.serial)
        return {"serial": self.serial}


test_server = thp.ModuleLevelServer(store)

setUp = test_server.setUp
tearDown = test_server.tearDown

describe AsyncTestCase, "Commands":
    use_default_loop = True

    def command(self, command):
        serial = "d073d5{:06d}".format(random.randrange(1, 9999))
        cmd = {"command": command, "args": {"serial": serial}}
        return cmd, serial

    @test_server.test
    async it "has progress cb functionality for http", options, fake, server:
        command, serial = self.command("test_no_error")
        await server.assertPUT(
            self, "/v1/lifx/command", command, status=200, json_output={"serial": serial}
        )

        command, serial = self.command("test_error")
        await server.assertPUT(
            self, "/v1/lifx/command", command, status=200, json_output={"serial": serial}
        )

        command, serial = self.command("test_done_progress")
        await server.assertPUT(
            self, "/v1/lifx/command", command, status=200, json_output={"serial": serial}
        )

    @test_server.test
    async it "has progress cb functionality for websockets", options, fake, server:
        async with server.ws_stream(self) as stream:

            # Done progress
            command, serial = self.command("test_done_progress")
            await stream.start("/v1/lifx/command", command)
            await stream.check_reply({"progress": {"done": True, "serial": serial}})
            await stream.check_reply({"serial": serial})

            # No error
            command, serial = self.command("test_no_error")
            await stream.start("/v1/lifx/command", command)
            await stream.check_reply({"progress": {"info": "hello", "serial": serial}})
            await stream.check_reply({"progress": {"info": "there"}})
            await stream.check_reply({"serial": serial})

            # With error
            command, serial = self.command("test_error")
            await stream.start("/v1/lifx/command", command)
            await stream.check_reply(
                {"progress": {"error": "Nope", "error_code": "Exception", "serial": serial}}
            )
            await stream.check_reply({"progress": {"error": "Yeap", "error_code": "ValueError"}})
            await stream.check_reply(
                {
                    "progress": {
                        "error": {"message": "a problem. wat", "one": 1},
                        "error_code": "Problem",
                        "serial": serial,
                    }
                }
            )
            await stream.check_reply({"serial": serial})

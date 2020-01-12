from photons_interactor.commander import test_helpers as cthp
from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_app.formatter import MergedOptionStringFormatter

from photons_tile_paint.options import GlobalOptions
from photons_control import test_helpers as chp
from photons_messages import protocol_register

from whirlwind import test_helpers as wthp
from unittest import mock
import tempfile
import logging
import asyncio
import pytest
import shutil
import uuid

log = logging.getLogger("photons_interactor.test_helpers")


class Asserter:
    def assertEqual(s, a, b, msg=None):
        __tracebackhide__ = True
        if msg:
            assert a == b, msg
        else:
            assert a == b

    def assertIs(s, a, b, msg=None):
        __tracebackhide__ = True
        if msg:
            assert a is b, msg
        else:
            assert a is b


@pytest.fixture(scope="session")
def asserter():
    return Asserter()


@pytest.fixture(scope="session")
def temp_dir_maker():
    class Maker:
        def __enter__(s):
            s.dir = tempfile.mkdtemp()
            return s.dir

        def __exit__(s, exc_type, exc, tb):
            if hasattr(s, "dir") and s.dir:
                shutil.rmtree(s.dir)

    return Maker


@pytest.fixture(scope="session")
async def server_wrapper():
    return ServerWrapper


@pytest.fixture(scope="session")
def options_maker():
    return make_options


@pytest.fixture(scope="session")
def fake():
    return cthp.fakery


def make_options(
    host=None, port=None, device_finder_options=None, database=None, cookie_secret=None
):
    options = {"database": database or {"uri": "sqlite:///:memory:"}}

    if device_finder_options is not None:
        options["device_finder_options"] = device_finder_options

    if cookie_secret is not None:
        options["cookie_secret"] = cookie_secret

    if host is not None:
        options["host"] = host

    if port is not None:
        options["port"] = port

    return Options.FieldSpec(formatter=MergedOptionStringFormatter).empty_normalise(**options)


async def make_server_runner(store, target_register=None, **kwargs):
    final_future = asyncio.Future()

    if "device_finder_options" not in kwargs:
        kwargs["device_finder_options"] = {"repeat_spread": 0.01}
    options = make_options("127.0.0.1", wthp.free_port(), **kwargs)

    targetrunner = chp.MemoryTargetRunner(final_future, cthp.fakery.devices)
    await targetrunner.start()

    if target_register is None:
        target_register = mock.Mock(name="target_register")

        def resolve(name):
            assert name == "lan", name
            return targetrunner.target

        target_register.resolve.side_effect = resolve

    cleaners = []
    server = Server(final_future, store=store)

    runner = ServerRunner(
        final_future,
        options.port,
        server,
        None,
        cthp.fakery,
        options,
        cleaners,
        target_register,
        protocol_register,
        GlobalOptions.create(),
    )
    return runner, server, options


class ServerRunner(wthp.ServerRunner):
    def setup(self, fake, *args, **kwargs):
        self.fake = fake
        self.options = args[0]
        super().setup(*args, **kwargs)

    async def after_close(self, exc_typ, exc, tb):
        if hasattr(self.server.finder.finish, "mock_calls"):
            assert len(self.server.finder.finish.mock_calls) == 0

        for thing in self.server.cleaners:
            try:
                await thing()
            except:
                pass

        # Prevent coroutine not awaited error
        await asyncio.sleep(0.01)

        if hasattr(self.server.finder.finish, "mock_calls"):
            self.server.finder.finish.assert_called_once_with()


class ServerWrapper:
    def __init__(self, store, **kwargs):
        self.store = store
        self.kwargs = kwargs

    async def __aenter__(self):
        return await self.start()

    async def start(self):
        self.runner, self.server, self.options = await make_server_runner(self.store, **self.kwargs)
        await self.runner.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.finish()

    async def finish(self):
        _, nd = await asyncio.wait([self.runner.close(None, None, None)])
        if nd:
            assert False, "Failed to shutdown the runner"

    def test_wrap(self):
        class Wrap:
            async def __aenter__(s):
                for device in cthp.fakery.devices:
                    await device.reset()

            async def __aexit__(s, exc_typ, exc, tb):
                pass

        return Wrap()

    def ws_stream(self):
        class WSStream(wthp.WSStream):
            async def start(s, command, serial, **other_args):
                s.message_id = str(uuid.uuid1())
                body = {"command": command, "args": {"serial": serial, **other_args}}
                await s.server.ws_write(
                    s.connection,
                    {"path": "/v1/lifx/command", "body": body, "message_id": s.message_id},
                )

        return WSStream(self.runner, Asserter())

    async def assertCommand(
        self, command, status=200, json_output=None, text_output=None, timeout=None
    ):
        return await self.runner.assertPUT(
            Asserter(),
            "/v1/lifx/command",
            command,
            status=status,
            json_output=json_output,
            text_output=text_output,
        )

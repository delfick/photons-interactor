from photons_interactor.commander import test_helpers as cthp
from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_app.formatter import MergedOptionStringFormatter
from photons_app.test_helpers import AsyncTestCase

from photons_messages import protocol_register

from whirlwind import test_helpers as thp
from unittest import mock
import tempfile
import asyncio
import shutil
import os

def make_options(host=None, port=None, device_finder_options=None, database=None, cookie_secret=None):
    options = {
          "database": database or {"uri": "sqlite:///:memory:"}
        }

    if device_finder_options is not None:
        options["device_finder_options"] = device_finder_options

    if cookie_secret is not None:
        options["cookie_secret"] = cookie_secret

    if host is not None:
        options['host'] = host

    if port is not None:
        options['port'] = port

    return Options.FieldSpec(formatter=MergedOptionStringFormatter).empty_normalise(**options)

class ServerRunner(thp.ServerRunner):
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

    async def started_test(self):
        self.fake.reset_devices()

def make_server(store, wrapper, **kwargs):
    final_future = asyncio.Future()

    if "device_finder_options" not in kwargs:
        kwargs["device_finder_options"] = {"repeat_spread": 0.01}
    options = make_options("127.0.0.1", thp.free_port(), **kwargs)

    lan_target = cthp.make_memory_target(final_future)

    target_register = mock.Mock(name="target_register")
    target_register.resolve.return_value = lan_target

    fake = cthp.fake_devices(protocol_register)

    cleaners = []
    server = Server(final_future, store=store)

    targetrunner = cthp.MemoryTargetRunner(lan_target, fake["devices"])
    server = ServerRunner(final_future, options.port, server, wrapper
        , fake, options, cleaners, target_register, protocol_register
        )
    return targetrunner, server

class ModuleLevelServer(thp.ModuleLevelServer):
    async def server_runner(self, store, wrapper=None):
        self.reportdir = tempfile.mkdtemp()
        targetrunner, runner = make_server(store, wrapper)
        await targetrunner.start()
        await runner.start()

        async def closer():
            try:
                await runner.closer()
            finally:
                await targetrunner.close()
                if os.path.exists(self.reportdir):
                    shutil.rmtree(self.reportdir)

        return runner, closer

    async def run_test(self, func):
        return await func(self.runner.options, self.runner.fake, self.runner)

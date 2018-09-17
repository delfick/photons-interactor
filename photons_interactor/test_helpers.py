from photons_interactor.commander import test_helpers as cthp
from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_app.formatter import MergedOptionStringFormatter
from photons_app.test_helpers import AsyncTestCase
from photons_app import helpers as hp

from tornado.websocket import websocket_connect
from contextlib import contextmanager
from functools import partial
from unittest import mock
import http.client
import tempfile
import logging
import asyncio
import socket
import shutil
import uuid
import time
import json
import os

log = logging.getLogger("photons_interactor.test_helpers")

def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 0))
        return s.getsockname()[1]

def port_connected(port):
    s = socket.socket()
    s.settimeout(5)
    try:
        s.connect(("127.0.0.1", port))
        s.close()
        return True
    except Exception:
        return False

class WSStream:
    def __init__(self, server, test):
        self.test = test
        self.server = server

    async def __aenter__(self):
        self.connection = await self.server.ws_connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if hasattr(self, "connection"):
            self.connection.close()
            try:
                self.test.assertIs(await self.server.ws_read(self.connection), None)
            except AssertionError:
                if exc_type is not None:
                    exc.__traceback__ = tb
                    raise exc
                raise

    async def start(self, command, **other_args):
        self.msg_id = str(uuid.uuid1())
        body = {"command": command, "args": {**other_args}}
        await self.server.ws_write(self.connection, {"path": "/v1/lifx/command", "body": body, "message_id": self.msg_id})

    async def check_reply(self, reply):
        d, nd = await asyncio.wait([self.server.ws_read(self.connection)], timeout=5)
        if nd:
            assert False, "Timedout waiting for future"

        got = await list(d)[0]
        wanted = {"message_id": self.msg_id, "reply": reply}
        if got != wanted:
            print("got --->")
            print(got)
            print("wanted --->")
            print(wanted)

        self.test.assertEqual(got, wanted)

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

class ServerRunner:
    def __init__(self, final_future, server, fake, options, wrapper):
        if wrapper is None:
            @contextmanager
            def wrapper():
                yield
            wrapper = wrapper()

        self.fake = fake
        self.server = server
        self.options = options
        self.wrapper = wrapper
        self.final_future = final_future

    async def run(self, runner):
        await runner(self.options, self.fake, self)

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, typ, exc, tb):
        await self.close(typ, exc, tb)

    async def start(self):
        async def doit():
            with self.wrapper:
                await self.server.serve()
        assert not port_connected(self.options.port)
        self.t = hp.async_as_background(doit())

        start = time.time()
        while time.time() - start < 5:
            if port_connected(self.options.port):
                break
            await asyncio.sleep(0.001)
        assert port_connected(self.options.port)
        return self

    async def close(self, typ, exc, tb):
        if typ is not None:
            log.error("Something went wrong", exc_info=(typ, exc, tb))

        self.final_future.cancel()
        if not hasattr(self, "t"):
            return

        if self.t is not None and not self.t.done():
            try:
                await asyncio.wait_for(self.t, timeout=5)
            except asyncio.CancelledError:
                pass

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

        assert not port_connected(self.options.port)

    @property
    def ws_url(self):
        return f"ws://127.0.0.1:{self.options.port}/v1/ws"

    async def ws_connect(self):
        connection = await websocket_connect(self.ws_url)

        class ATime:
            def __eq__(self, other):
                return type(other) is float

        first = await self.ws_read(connection)
        assert first == {"reply": ATime(), "message_id": "__server_time__"}, first

        return connection

    async def ws_write(self, connection, message):
        return await connection.write_message(json.dumps(message))

    async def ws_read(self, connection):
        res = await connection.read_message()
        if res is None:
            return res
        return json.loads(res)

class CommandCase(AsyncTestCase):
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
                if json_output is not None:
                    self.maxDiff = None
                    try:
                        self.assertEqual(json.loads(body.decode()), json_output)
                    except AssertionError:
                        print(json.dumps(json.loads(body.decode()), sort_keys=True, indent="    "))
                        raise
                else:
                    self.assertEqual(body, text_output)
        return await self.wait_for(self.loop.run_in_executor(None, doit), timeout=timeout)

    async def run_server(self, wrapper, runner, **kwargs):
        self.maxDiff = None
        targetrunner, server = make_server(wrapper, **kwargs)
        async with targetrunner:
            async with server:
                await server.run(runner)

def make_server(wrapper, **kwargs):
    final_future = asyncio.Future()

    protocol_register = cthp.make_protocol_register()
    if "device_finder_options" not in kwargs:
        kwargs["device_finder_options"] = {"repeat_spread": 0.01}
    options = make_options("127.0.0.1", free_port(), **kwargs)

    lan_target = cthp.make_memory_target(final_future)

    target_register = mock.Mock(name="target_register")
    target_register.resolve.return_value = lan_target

    fake = cthp.fake_devices(protocol_register)

    cleaners = []
    server = Server(final_future, options, cleaners, target_register, protocol_register)

    targetrunner = cthp.MemoryTargetRunner(lan_target, fake["devices"])
    server = ServerRunner(final_future, server, fake, options, wrapper)
    return targetrunner, server

class ModuleLevelServer:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.server = None
        self.closer = None
        self.record_lines_read = 0

    def setUp(self):
        async def setup():
            self.reportdir = tempfile.mkdtemp()
            targetrunner, server = make_server(None)
            await targetrunner.start()
            await server.start()

            async def closer():
                _, nd = await asyncio.wait([server.close(None, None, None)], timeout=5)
                await targetrunner.close()
                if os.path.exists(self.reportdir):
                    shutil.rmtree(self.reportdir)
                if nd:
                    assert False, "Failed to shutdown the server"

            return server, closer
        asyncio.set_event_loop(self.loop)
        self.server, self.closer = self.loop.run_until_complete(setup())

    def tearDown(self):
        if self.closer is not None:
            self.loop.run_until_complete(self.closer())
        self.loop.close()
        asyncio.set_event_loop(None)

    def test(self, func):
        async def test(s):
            self.server.fake.reset_devices()
            s.maxDiff = None
            await s.wait_for(self.server.run(partial(func, s)), timeout=10)

        test.__name__ = func.__name__
        return test

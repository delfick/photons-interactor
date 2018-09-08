from photons_interactor.commander import test_helpers as cthp
from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_app.formatter import MergedOptionStringFormatter
from photons_app.test_helpers import AsyncTestCase
from photons_app import helpers as hp

from tornado.websocket import websocket_connect
from input_algorithms.dictobj import dictobj
from input_algorithms.meta import Meta
from option_merge import MergedOptions
from contextlib import contextmanager
from unittest import mock
import http.client
import asyncio
import socket
import time
import json

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
    def __init__(self, final_future, server, options, wrapper):
        if wrapper is None:
            @contextmanager
            def wrapper():
                yield
            wrapper = wrapper()

        self.server = server
        self.options = options
        self.wrapper = wrapper
        self.final_future = final_future

    async def __aenter__(self):
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

    async def __aexit__(self, typ, exc, tb):
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
        final_future = asyncio.Future()

        protocol_register = cthp.make_protocol_register()
        options = make_options("127.0.0.1", free_port(), **kwargs)

        lan_target = cthp.make_memory_target(final_future)

        target_register = mock.Mock(name="target_register")
        target_register.resolve.return_value = lan_target

        fake = cthp.fake_devices(protocol_register)

        cleaners = []
        server = Server(final_future, options, cleaners, target_register, protocol_register)

        self.maxDiff = None

        async with cthp.MemoryTargetRunner(lan_target, fake["devices"]):
            async with ServerRunner(final_future, server, options, wrapper) as s:
                await runner(options, fake, s)

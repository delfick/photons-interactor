from photons_app import helpers as hp

from tornado.websocket import websocket_connect
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

class ServerRunner:
    def __init__(self, final_future, server, options, wrapper):
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

        if hasattr(self.server.finder.finish, "mock_calls"):
            self.server.finder.finish.assert_called_once_with()

        assert not port_connected(self.options.port)

    @property
    def ws_url(self):
        return f"ws://127.0.0.1:{self.options.port}/v1/ws"

    async def ws_connect(self):
        return await websocket_connect(self.ws_url)

    async def ws_write(self, connection, message):
        return await connection.write_message(json.dumps(message))

    async def ws_read(self, connection):
        res = await connection.read_message()
        if res is None:
            return res
        return json.loads(res)

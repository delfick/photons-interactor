# coding: spec

from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_app.test_helpers import AsyncTestCase
from photons_app import helpers as hp

from noseOfYeti.tokeniser.async_support import async_noy_sup_setUp, async_noy_sup_tearDown
from unittest import mock
import http.client
import asynctest
import asyncio
import socket
import time

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
    except Exception as error:
        return False

describe AsyncTestCase, "Server":
    async it "takes in options":
        final_future = mock.Mock(name="final_future")
        server_options = mock.Mock(name="server_options")
        cleaners = mock.Mock(name="cleaners")
        target_register = mock.Mock(name="target_register")
        protocol_register = mock.Mock(name="protocol_register")

        server = Server(final_future, server_options, cleaners, target_register, protocol_register)

        self.assertIs(server.final_future, final_future)
        self.assertIs(server.server_options, server_options)
        self.assertIs(server.cleaners, cleaners)
        self.assertIs(server.target_register, target_register)
        self.assertIs(server.protocol_register, protocol_register)

    describe "serve":
        async before_each:
            self.final_future = asyncio.Future()

            self.target_register = mock.Mock(name="target_register")
            self.protocol_register = mock.Mock(name="protocol_register")

        async after_each:
            # Make sure the server dies
            if hasattr(self, "final_future"):
                self.final_future.cancel()

        async def assertPUTCommand(self, options, commander):
            commander.execute = asynctest.mock.CoroutineMock(name="execute", return_value={})

            def doit():
                conn = http.client.HTTPConnection("127.0.0.1", options.port, timeout=5)
                conn.request("PUT", "/v1/lifx/command", body=b'{"command": "wat"}')
                res = conn.getresponse()

                self.assertEqual(res.status, 200)
                self.assertEqual(res.read(), b"{}")
            await self.wait_for(self.loop.run_in_executor(None, doit))

            commander.execute.assert_called_once_with({"command": "wat"})

        async it "works":
            options = Options.FieldSpec().empty_normalise(
                  host = "127.0.0.1"
                , port = free_port()
                )

            lan_target = mock.Mock(name="lan_target")
            self.target_register.resolve.return_value = lan_target

            finder = mock.Mock(name="finder")
            finder.start = asynctest.mock.CoroutineMock(name="start")
            finder.finish = asynctest.mock.CoroutineMock(name="finish")
            FakeDeviceFinder = mock.Mock(name="DeviceFinder", return_value=finder)

            commander = mock.Mock(name="commander")
            FakeCommander = mock.Mock(name="Commander", return_value=commander)

            cleaners = []
            server = Server(self.final_future, options, cleaners, self.target_register, self.protocol_register)

            async def doit():
                with mock.patch("photons_interactor.server.Commander", FakeCommander):
                    with mock.patch("photons_interactor.server.DeviceFinder", FakeDeviceFinder):
                        await server.serve()

            assert not port_connected(options.port)
            t = hp.async_as_background(doit())

            try:
                start = time.time()
                while time.time() - start < 5:
                    if port_connected(options.port):
                        break
                    await asyncio.sleep(1)
                assert port_connected(options.port)

                await self.assertPUTCommand(options, commander)
            finally:
                self.final_future.cancel()
                try:
                    await t
                except asyncio.CancelledError:
                    pass

                self.assertEqual(len(finder.finish.mock_calls), 0)

                for thing in cleaners:
                    try:
                        await thing()
                    except:
                        pass

                finder.finish.assert_called_once_with()

            assert not port_connected(options.port)

            self.assertIs(server.commander, commander)
            self.assertIs(server.finder, finder)

            FakeCommander.assert_called_once_with(finder, self.target_register, self.protocol_register)
            FakeDeviceFinder.assert_called_once_with(lan_target)
            self.target_register.resolve.assert_called_once_with("lan")
            finder.start.assert_called_once_with()

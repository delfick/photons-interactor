# coding: spec

from photons_interactor.commander.commands.animations import AnimationsStore
from photons_interactor import test_helpers as thp
from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_app.test_helpers import AsyncTestCase
from photons_app import helpers as hp

from noseOfYeti.tokeniser.async_support import async_noy_sup_setUp, async_noy_sup_tearDown
from tornado.httpclient import AsyncHTTPClient
from whirlwind import test_helpers as wthp
from contextlib import contextmanager
from unittest import mock
import asynctest
import asyncio

describe AsyncTestCase, "Server":
    describe "serve":
        async before_each:
            self.final_future = asyncio.Future()

            self.target_register = mock.Mock(name="target_register")
            self.protocol_register = mock.Mock(name="protocol_register")

        async after_each:
            # Make sure the server dies
            if hasattr(self, "final_future"):
                self.final_future.cancel()

        async def assertIndex(self, options):
            client = AsyncHTTPClient()

            response = await client.fetch(f"http://127.0.0.1:{options.port}/"
                , raise_error=False
                )

            self.assertEqual(response.code, 200, response.body)
            assert response.body.startswith(b"<!DOCTYPE html>"), response.body

            self.assertEqual(response.headers['Content-Type'], "text/html; charset=UTF-8")

        async it "works":
            options = thp.make_options("127.0.0.1", wthp.free_port()
                , device_finder_options = {"arg1": 0.1, "arg2": True}
                )

            lan_target = mock.Mock(name="lan_target")
            self.target_register.resolve.return_value = lan_target

            finder = mock.Mock(name="finder")
            finder.start = asynctest.mock.CoroutineMock(name="start")
            finder.finish = asynctest.mock.CoroutineMock(name="finish")
            FakeDeviceFinder = mock.Mock(name="DeviceFinder", return_value=finder)

            db_queue = mock.Mock(name="db_queue")
            FakeDBQueue = mock.Mock(name="DBQueue", return_value=db_queue)

            commander = mock.Mock(name="commander")
            FakeCommander = mock.Mock(name="Commander", return_value=commander)

            cleaners = []
            server = Server(self.final_future)

            @contextmanager
            def wrapper():
                with mock.patch("photons_interactor.server.Commander", FakeCommander):
                    with mock.patch("photons_interactor.server.DeviceFinder", FakeDeviceFinder):
                        with mock.patch("photons_interactor.server.DBQueue", FakeDBQueue):
                            yield

            async with thp.ServerRunner(self.final_future, options.port, server, wrapper(), None, options, cleaners,self.target_register, self.protocol_register) as s:
                commander.executor.return_value.execute = asynctest.mock.CoroutineMock(name="execute", return_value={})
                await s.assertPUT(self, "/v1/lifx/command", {"command": "wat"}, json_output={})

                await self.assertIndex(options)

            self.assertIs(server.commander, commander)
            self.assertIs(server.finder, finder)
            self.assertIsInstance(server.animations, AnimationsStore)

            from photons_interactor.commander.store import store

            FakeCommander.assert_called_once_with(store
                , finder = finder
                , db_queue = db_queue
                , animations = server.animations
                , test_devices = None
                , final_future = self.final_future
                , server_options = options
                , target_register = self.target_register
                , protocol_register = self.protocol_register
                )
            FakeDeviceFinder.assert_called_once_with(lan_target, arg1=0.1, arg2=True)
            FakeDBQueue.assert_called_once_with(self.final_future, 5, mock.ANY, "sqlite:///:memory:")

            self.target_register.resolve.assert_called_once_with("lan")
            finder.start.assert_called_once_with()
            db_queue.start.assert_called_once_with()

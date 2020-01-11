# coding: spec

from photons_interactor.request_handlers.command import better_reprer, MessageFromExc
from photons_interactor.commander import helpers as chp
from photons_interactor import test_helpers as thp
from photons_interactor.server import Server

from photons_app.test_helpers import AsyncTestCase
from photons_app.errors import PhotonsAppError
from photons_app import helpers as hp

from photons_tile_paint.options import GlobalOptions

from whirlwind.request_handlers.base import SimpleWebSocketBase
from whirlwind.server import wait_for_futures
from whirlwind import test_helpers as wthp
from contextlib import contextmanager
from unittest import mock
import asynctest
import asyncio
import socket
import types
import time
import uuid


class SimpleWebSocketBase(SimpleWebSocketBase):
    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.reprer = better_reprer
        self.message_from_exc = MessageFromExc()


class WSServer(thp.ServerRunner):
    def __init__(self, Handler, handler_args=None):
        self.final_future = asyncio.Future()
        self.protocol_register = mock.Mock(name="protocol_register")
        self.options = thp.make_options("127.0.0.1", wthp.free_port())

        self.wsconnections = {}
        handler_args = {"server_time": time.time()} if handler_args is None else handler_args
        if "wsconnections" not in handler_args:
            handler_args["wsconnections"] = self.wsconnections

        class WSS(Server):
            def tornado_routes(self):
                return [("/v1/ws", Handler, handler_args)]

        self.lan_target = mock.Mock(name="lan_target")
        self.target_register = mock.Mock(name="target_register")
        self.target_register.resolve.return_value = self.lan_target

        self.protocol_register = mock.Mock(name="protocol_register")

        self.cleaners = []
        self.server = WSS(self.final_future)

        self.finder = mock.Mock(name="finder")
        self.finder.start = asynctest.mock.CoroutineMock(name="start")
        self.finder.finish = asynctest.mock.CoroutineMock(name="finish")
        FakeDeviceFinder = mock.Mock(name="DeviceFinder", return_value=self.finder)

        @contextmanager
        def wrapper():
            with mock.patch("photons_interactor.server.DeviceFinder", FakeDeviceFinder):
                yield

        super().__init__(
            self.final_future,
            self.options.port,
            self.server,
            wrapper(),
            None,
            self.options,
            self.cleaners,
            self.target_register,
            self.protocol_register,
            GlobalOptions.create(),
        )

    async def after_close(self, exc_type, exc, tb):
        await super().after_close(exc_type, exc, tb)
        await wait_for_futures(self.wsconnections)


describe AsyncTestCase, "SimpleWebSocketBase":
    async it "can handle a ResultBuilder":

        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, message_key, progress_cb):
                return chp.ResultBuilder(serials=["d073d5000001"])

        async def doit():
            async with WSServer(Handler) as server:
                connection = await server.ws_connect()

                msg_id = str(uuid.uuid1())
                await server.ws_write(
                    connection, {"path": "/thing", "body": {}, "message_id": msg_id}
                )
                assert await server.ws_read(connection) == {
                    "message_id": msg_id,
                    "reply": {"results": {"d073d5000001": "ok"}},
                }

                connection.close()
                assert await server.ws_read(connection) is None

        await self.wait_for(doit())

    async it "can process replies":
        replies = []

        error1 = ValueError("Bad things happen")
        error2 = PhotonsAppError("Stuff")
        error3 = TypeError("NOPE")
        error4 = PhotonsAppError("Blah")
        error5 = PhotonsAppError("things", serial="d073d5000001")

        class Handler(SimpleWebSocketBase):
            def process_reply(self, msg, exc_info=None):
                replies.append((msg, exc_info))

            async def process_message(s, path, body, message_id, message_key, progress_cb):
                if path == "/no_error":
                    return {"success": True}
                elif path == "/internal_error":
                    raise error1
                elif path == "/builder_error":
                    builder = chp.ResultBuilder(["d073d5000001"])
                    builder.error(error2)
                    s.reply({"progress": {"error": "progress"}}, message_id=message_id)
                    return builder
                elif path == "/builder_serial_error":
                    builder = chp.ResultBuilder(["d073d5000001"])
                    try:
                        raise error5
                    except Exception as e:
                        builder.error(e)
                    return builder
                elif path == "/builder_internal_error":
                    builder = chp.ResultBuilder(["d073d5000001"])
                    try:
                        raise error3
                    except Exception as error:
                        builder.error(error)
                    return builder
                elif path == "/error":
                    raise error4

        async def doit():
            self.maxDiff = None

            async with WSServer(Handler) as server:
                connection = await server.ws_connect()

                ##################
                ### NO_ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(
                    connection, {"path": "/no_error", "body": {}, "message_id": msg_id}
                )
                assert await server.ws_read(connection) == {
                    "message_id": msg_id,
                    "reply": {"success": True},
                }

                ##################
                ### INTERNAL_ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(
                    connection, {"path": "/internal_error", "body": {}, "message_id": msg_id}
                )
                assert await server.ws_read(connection) == {
                    "message_id": msg_id,
                    "reply": {
                        "error": "Internal Server Error",
                        "error_code": "InternalServerError",
                        "status": 500,
                    },
                }

                ##################
                ### BUILDER_ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(
                    connection, {"path": "/builder_error", "body": {}, "message_id": msg_id}
                )
                assert await server.ws_read(connection) == {
                    "message_id": msg_id,
                    "reply": {"progress": {"error": "progress"}},
                }

                assert await server.ws_read(connection) == {
                    "message_id": msg_id,
                    "reply": {
                        "results": {"d073d5000001": "ok"},
                        "errors": [
                            {
                                "error": {"message": "Stuff"},
                                "error_code": "PhotonsAppError",
                                "status": 400,
                            }
                        ],
                    },
                }

                ##################
                ### BUILDER_SERIAL_ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(
                    connection, {"path": "/builder_serial_error", "body": {}, "message_id": msg_id}
                )

                assert await server.ws_read(connection) == {
                    "message_id": msg_id,
                    "reply": {
                        "results": {
                            "d073d5000001": {
                                "error": {"message": "things"},
                                "error_code": "PhotonsAppError",
                                "status": 400,
                            }
                        }
                    },
                }

                ##################
                ### BUILDER_INTERNAL_ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(
                    connection,
                    {"path": "/builder_internal_error", "body": {}, "message_id": msg_id},
                )
                assert await server.ws_read(connection) == {
                    "message_id": msg_id,
                    "reply": {
                        "results": {"d073d5000001": "ok"},
                        "errors": [
                            {
                                "error": "Internal Server Error",
                                "error_code": "InternalServerError",
                                "status": 500,
                            }
                        ],
                    },
                }

                ##################
                ### ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(
                    connection, {"path": "/error", "body": {}, "message_id": msg_id}
                )
                assert await server.ws_read(connection) == {
                    "message_id": msg_id,
                    "reply": {
                        "error": {"message": "Blah"},
                        "error_code": "PhotonsAppError",
                        "status": 400,
                    },
                }

                connection.close()
                assert await server.ws_read(connection) is None

        await self.wait_for(doit())

        class ATraceback:
            def __eq__(self, other):
                return isinstance(other, types.TracebackType)

        self.maxDiff = None

        assert replies == [
            ({"success": True}, None),
            (
                {
                    "status": 500,
                    "error": "Internal Server Error",
                    "error_code": "InternalServerError",
                },
                (ValueError, error1, ATraceback()),
            ),
            ({"progress": {"error": "progress"}}, None),
            (
                {
                    "results": {"d073d5000001": "ok"},
                    "errors": [
                        {
                            "error": {"message": "Stuff"},
                            "error_code": "PhotonsAppError",
                            "status": 400,
                        }
                    ],
                },
                {None: [(PhotonsAppError, error2, None)]},
            ),
            (
                {
                    "results": {
                        "d073d5000001": {
                            "error": {"message": "things"},
                            "error_code": "PhotonsAppError",
                            "status": 400,
                        }
                    }
                },
                {"d073d5000001": (PhotonsAppError, error5, ATraceback())},
            ),
            (
                {
                    "results": {"d073d5000001": "ok"},
                    "errors": [
                        {
                            "error": "Internal Server Error",
                            "error_code": "InternalServerError",
                            "status": 500,
                        }
                    ],
                },
                {None: [(TypeError, error3, ATraceback())]},
            ),
            (
                {"error": {"message": "Blah"}, "error_code": "PhotonsAppError", "status": 400},
                (PhotonsAppError, error4, ATraceback()),
            ),
        ]

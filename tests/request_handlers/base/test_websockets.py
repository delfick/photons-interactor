# coding: spec

from photons_interactor.request_handlers.base import SimpleWebSocketBase, wsconnections
from photons_interactor.commander import helpers as chp
from photons_interactor import test_helpers as thp
from photons_interactor.server import Server

from photons_app.test_helpers import AsyncTestCase
from photons_app.errors import PhotonsAppError
from photons_app import helpers as hp

from contextlib import contextmanager
from unittest import mock
import asynctest
import asyncio
import socket
import types
import time
import uuid

class WSServer(thp.ServerRunner):
    def __init__(self, Handler, handler_args=None):
        self.final_future = asyncio.Future()
        self.protocol_register = mock.Mock(name="protocol_register")
        self.options = thp.make_options("127.0.0.1", thp.free_port())

        class WSS(Server):
            def tornado_routes(self):
                return [("/v1/ws", Handler, {"server_time": time.time()} if handler_args is None else handler_args)]

        self.lan_target = mock.Mock(name="lan_target")
        self.target_register = mock.Mock(name="target_register")
        self.target_register.resolve.return_value = self.lan_target

        self.protocol_register = mock.Mock(name="protocol_register")

        self.cleaners = []
        self.server = WSS(self.final_future, self.options, self.cleaners, self.target_register, self.protocol_register)

        self.finder = mock.Mock(name="finder")
        self.finder.start = asynctest.mock.CoroutineMock(name="start")
        self.finder.finish = asynctest.mock.CoroutineMock(name="finish")
        FakeDeviceFinder = mock.Mock(name="DeviceFinder", return_value=self.finder)

        @contextmanager
        def wrapper():
            with mock.patch("photons_interactor.server.DeviceFinder", FakeDeviceFinder):
                yield

        super().__init__(self.final_future, self.server, None, self.options, wrapper())

describe AsyncTestCase, "SimpleWebSocketBase":
    async it "stores a task in wsconnections":
        self.assertEqual(wsconnections, {})

        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, progress_cb):
                self.assertEqual(type(self.key), str)
                self.assertEqual(len(self.key), 36)
                assert self.key in wsconnections
                return "blah"

        async def doit():
            message_id = str(uuid.uuid1())

            async with WSServer(Handler) as server:
                connection = await server.ws_connect()
                await server.ws_write(connection
                    , {"path": "/one/two", "body": {"hello": "there"}, "message_id": message_id}
                    )
                res = await server.ws_read(connection)
                self.assertEqual(wsconnections, {})

                connection.close()
                self.assertIs(await server.ws_read(connection), None)

        await self.wait_for(doit())

    async it "waits for connections to close before ending server":
        f1 = asyncio.Future()
        f2 = asyncio.Future()

        self.assertEqual(wsconnections, {})

        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, progress_cb):
                f1.set_result(True)
                await asyncio.sleep(0.5)
                f2.set_result(True)
                return "blah"

        async def doit():
            message_id = str(uuid.uuid1())

            async with WSServer(Handler) as server:
                connection = await server.ws_connect()
                await server.ws_write(connection
                    , {"path": "/one/two", "body": {"hello": "there"}, "message_id": message_id}
                    )
                await self.wait_for(f1)
                self.assertEqual(len(wsconnections), 1)
                assert not f2.done()

            self.assertEqual(len(wsconnections), 0)
            self.assertEqual(f2.result(), True)

        await self.wait_for(doit())

    async it "has ws_connection object":
        f = asyncio.Future()

        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, progress_cb):
                s.reply({"one": "two"}, message_id=message_id)
                assert hasattr(s, "ws_connection")
                f.set_result(True)
                return "blah"

        async def doit():
            message_id = str(uuid.uuid1())

            async with WSServer(Handler) as server:
                connection = await server.ws_connect()
                await server.ws_write(connection
                    , {"path": "/one/two", "body": {"hello": "there"}, "message_id": message_id}
                    )
                res = await server.ws_read(connection)
                self.assertEqual(res["message_id"], message_id)
                self.assertEqual(res["reply"], {"one": "two"})

                await f

                res = await server.ws_read(connection)
                self.assertEqual(res["message_id"], message_id)
                self.assertEqual(res["reply"], "blah")

                connection.close()
                self.assertIs(await server.ws_read(connection), None)

        await self.wait_for(doit())

    async it "can stay open":
        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, progress_cb):
                self.assertEqual(path, "/one/two")
                self.assertEqual(body, {"wat": mock.ANY})
                return body["wat"]

        async def doit():
            message_id = str(uuid.uuid1())

            async with WSServer(Handler) as server:
                connection = await server.ws_connect()
                await server.ws_write(connection
                    , {"path": "/one/two", "body": {"wat": "one"}, "message_id": message_id}
                    )
                res = await server.ws_read(connection)
                self.assertEqual(res["message_id"], message_id)
                self.assertEqual(res["reply"], "one")

                await server.ws_write(connection
                    , {"path": "/one/two", "body": {"wat": "two"}, "message_id": message_id}
                    )
                res = await server.ws_read(connection)
                self.assertEqual(res["message_id"], message_id)
                self.assertEqual(res["reply"], "two")

                connection.close()
                self.assertIs(await server.ws_read(connection), None)

        await self.wait_for(doit())

    async it "can handle ticks for me":
        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, progress_cb):
                self.assertEqual(path, "/one/two")
                self.assertEqual(body, {"wat": mock.ANY})
                return body["wat"]

        async def doit():
            message_id = str(uuid.uuid1())

            async with WSServer(Handler) as server:
                connection = await server.ws_connect()
                await server.ws_write(connection
                    , {"path": "__tick__", "message_id": "__tick__"}
                    )
                res = await server.ws_read(connection)
                self.assertEqual(res["message_id"], "__tick__")
                self.assertEqual(res["reply"], {"ok": "thankyou"})

                await server.ws_write(connection
                    , {"path": "/one/two", "body": {"wat": "two"}, "message_id": message_id}
                    )
                res = await server.ws_read(connection)
                self.assertEqual(res["message_id"], message_id)
                self.assertEqual(res["reply"], "two")

                connection.close()
                self.assertIs(await server.ws_read(connection), None)

        await self.wait_for(doit())

    async it "complains if the message is incorrect":
        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, progress_cb):
                return "processed"

        async def doit():
            invalid = [
                  {"message_id": "just_message_id"}
                , {"message_id": "no_path", "body": {}}
                , {"path": "/no/message_id", "body": {}}
                , {"path": "/no/body", "message_id": "blah"}
                , {}
                , ""
                , "asdf"
                , False
                , True
                , 0
                , 1
                , []
                , [1]
                ]

            async with WSServer(Handler) as server:
                connection = await server.ws_connect()

                for body in invalid:
                    await server.ws_write(connection, body)
                    res = await server.ws_read(connection)
                    assert res is not None, "Got no reply to : '{}'".format(body)
                    self.assertEqual(res["message_id"], None)
                    assert "reply" in res
                    assert "error" in res["reply"]

                connection.close()
                self.assertIs(await server.ws_read(connection), None)

        await self.wait_for(doit())

    async it "can do multiple messages at the same time":
        class Handler(SimpleWebSocketBase):
            do_close = False

            async def process_message(s, path, body, message_id, progress_cb):
                progress_cb({body["serial"]: ["info", "start"]})
                await asyncio.sleep(body["sleep"])
                return {"processed": body["serial"]}

        async def doit():
            async with WSServer(Handler) as server:
                connection = await server.ws_connect()

                msg_id1 = str(uuid.uuid1())
                msg_id2 = str(uuid.uuid1())

                await server.ws_write(connection
                    , {"path": "/process", "body": {"serial": "1", "sleep": 0.1}, "message_id": msg_id1}
                    )
                await server.ws_write(connection
                    , {"path": "/process", "body": {"serial": "2", "sleep": 0.05}, "message_id": msg_id2}
                    )

                self.assertEqual(await server.ws_read(connection)
                    , {"message_id": msg_id1, "reply": {"progress": {"1": ["info", "start"]}}}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , {"message_id": msg_id2, "reply": {"progress": {"2": ["info", "start"]}}}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , {"message_id": msg_id2, "reply": {"processed": "2"}}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , {"message_id": msg_id1, "reply": {"processed": "1"}}
                    )

                connection.close()
                self.assertIs(await server.ws_read(connection), None)

        await self.wait_for(doit())

    async it "can close the websocket if we return self.Closing":
        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, progress_cb):
                if body["close"]:
                    return s.Closing
                else:
                    return "stillalive"

        async def doit():
            async with WSServer(Handler) as server:
                connection = await server.ws_connect()

                msg_id = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/process", "body": {"close": False}, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , {"message_id": msg_id, "reply": "stillalive"}
                    )

                msg_id = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/process", "body": {"close": False}, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , {"message_id": msg_id, "reply": "stillalive"}
                    )

                msg_id = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/process", "body": {"close": True}, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , {"message_id": msg_id, "reply": {"closing": "goodbye"}}
                    )

                self.assertIs(await server.ws_read(connection), None)

        await self.wait_for(doit())

    async it "can handle arbitrary json for the body":
        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, progress_cb):
                return body

        async def doit():
            async with WSServer(Handler) as server:
                connection = await server.ws_connect()

                msg_id = str(uuid.uuid1())
                body = {
                      "one": "two"
                    , "three": 4
                    , "five": ["six", "seven", []]
                    , "six": []
                    , "seven": True
                    , "eight": False
                    , "nine": {"one": "two", "three": None, "four": {"five": "six"}}
                    }

                await server.ws_write(connection
                    , {"path": "/process", "body": body, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , {"message_id": msg_id, "reply": body}
                    )
                connection.close()

                self.assertIs(await server.ws_read(connection), None)

        await self.wait_for(doit())

    async it "can handle exceptions in process_message":
        class BadError(PhotonsAppError):
            desc = "nope"

        errors = {"one": ValueError("lolz"), "two": BadError("Try again", stuff=1)}

        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, progress_cb):
                raise errors[body["error"]]

        async def doit():
            async with WSServer(Handler) as server:
                connection = await server.ws_connect()

                msg_id = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/error", "body": {"error": "one"}, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , { "message_id": msg_id
                      , "reply":
                        { "error": "Internal Server Error"
                        , "error_code": "InternalServerError"
                        , "status": 500
                        }
                      }
                    )

                msg_id2 = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/error", "body": {"error": "two"}, "message_id": msg_id2}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , { "message_id": msg_id2
                      , "reply":
                        { "error": {"message": "nope. Try again", "stuff": 1}
                        , "error_code": "BadError"
                        , "status": 400
                        }
                      }
                    )

                connection.close()
                self.assertIs(await server.ws_read(connection), None)

        await self.wait_for(doit())

    async it "can handle a ResultBuilder":
        class Handler(SimpleWebSocketBase):
            async def process_message(s, path, body, message_id, progress_cb):
                return chp.ResultBuilder(serials=["d073d5000001"])

        async def doit():
            async with WSServer(Handler) as server:
                connection = await server.ws_connect()

                msg_id = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/thing", "body": {}, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , { "message_id": msg_id
                        , "reply": {"results": {"d073d5000001": "ok"}}
                      }
                    )

                connection.close()
                self.assertIs(await server.ws_read(connection), None)

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

            async def process_message(s, path, body, message_id, progress_cb):
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
                await server.ws_write(connection
                    , {"path": "/no_error", "body": {}, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , { "message_id": msg_id
                      , "reply": {"success": True}
                      }
                    )

                ##################
                ### INTERNAL_ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/internal_error", "body": {}, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , { "message_id": msg_id
                      , "reply": {"error": "Internal Server Error", "error_code": "InternalServerError", "status": 500}
                      }
                    )

                ##################
                ### BUILDER_ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/builder_error", "body": {}, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , { "message_id": msg_id
                      , "reply": {"progress": {"error": "progress"}}
                      }
                    )

                self.assertEqual(await server.ws_read(connection)
                    , { "message_id": msg_id
                      , 'reply':
                        { 'results': {'d073d5000001': 'ok'}
                        , 'errors':
                          [ {'error': {'message': 'Stuff'}, 'error_code': 'PhotonsAppError', "status": 400}
                          ]
                        }
                      }
                    )

                ##################
                ### BUILDER_SERIAL_ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/builder_serial_error", "body": {}, "message_id": msg_id}
                    )

                self.assertEqual(await server.ws_read(connection)
                    , { "message_id": msg_id
                      , 'reply':
                        { 'results':
                          { 'd073d5000001':
                            { 'error': {'message': 'things'}
                            , 'error_code': 'PhotonsAppError'
                            , "status": 400
                            }
                          }
                        }
                      }
                    )

                ##################
                ### BUILDER_INTERNAL_ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/builder_internal_error", "body": {}, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , { "message_id": msg_id
                      , "reply":
                        { "results": { "d073d5000001": "ok" }
                        , "errors":
                          [ { "error": "Internal Server Error", "error_code": "InternalServerError", "status": 500 }
                          ]
                        }
                      }
                    )

                ##################
                ### ERROR

                msg_id = str(uuid.uuid1())
                await server.ws_write(connection
                    , {"path": "/error", "body": {}, "message_id": msg_id}
                    )
                self.assertEqual(await server.ws_read(connection)
                    , { "message_id": msg_id
                      , "reply": {"error": {"message": "Blah"}, "error_code": "PhotonsAppError", "status": 400}
                      }
                    )

                connection.close()
                self.assertIs(await server.ws_read(connection), None)

        await self.wait_for(doit())

        class ATraceback:
            def __eq__(self, other):
                return isinstance(other, types.TracebackType)

        self.maxDiff = None

        self.assertEqual(replies
            , [ ( {'success': True}
                , None
                )
              , ( {'status': 500, 'error': 'Internal Server Error', 'error_code': 'InternalServerError'}
                , (ValueError, error1, ATraceback())
                )
              , ( {'progress': {'error': 'progress'}}
                , None
                )
              , ( { "results": {"d073d5000001": "ok"}
                  , "errors":
                    [ {'error': {'message': 'Stuff'}, 'error_code': 'PhotonsAppError', "status": 400}
                    ]
                  }
                , {None: [(PhotonsAppError, error2, None)]}
                )
              , ( { 'results':
                    { 'd073d5000001':
                      { 'error': {'message': 'things'}
                      , 'error_code': 'PhotonsAppError'
                      , "status": 400
                      }
                    }
                  }
                , {"d073d5000001": (PhotonsAppError, error5, ATraceback())}
                )
              , ( { "results": { "d073d5000001": "ok"}
                  , "errors":
                    [ {'error': 'Internal Server Error', 'error_code': 'InternalServerError', "status": 500}
                    ]
                  }
                , {None: [(TypeError, error3, ATraceback())]}
                )
              , ( {'error': {'message': 'Blah'}, 'error_code': 'PhotonsAppError', "status": 400}
                , (PhotonsAppError, error4, ATraceback())
                )
              ]
            )

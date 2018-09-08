# coding: spec

from photons_interactor.request_handlers.base import AsyncCatcher, Finished, message_from_exc

from photons_app.errors import PhotonsAppError

from noseOfYeti.tokeniser.async_support import async_noy_sup_setUp
from photons_app.test_helpers import AsyncTestCase
from delfick_error import DelfickError
from unittest import mock
import binascii
import bitarray
import asyncio
import types
import uuid

class ATraceback:
    def __eq__(self, other):
        return isinstance(other, types.TracebackType)

describe AsyncTestCase, "AsyncCatcher":
    async it "takes in the request, info and final":
        request = mock.Mock(name="request")
        info = mock.Mock(name="info")
        final = mock.Mock(name="final")
        catcher = AsyncCatcher(request, info, final=final)
        self.assertIs(catcher.request, request)
        self.assertIs(catcher.info, info)
        self.assertIs(catcher.final, final)

    async it "defaults final to None":
        request = mock.Mock(name="request")
        info = mock.Mock(name="info")
        catcher = AsyncCatcher(request, info)
        self.assertIs(catcher.info, info)
        self.assertIs(catcher.final, None)

    describe "Behaviour":
        async before_each:
            self.info = {}
            self.request = mock.Mock(name="request")
            self.catcher = AsyncCatcher(self.request, self.info)

        async it "completes with the result from info if no exception is raised":
            result = str(uuid.uuid1())

            fake_complete = mock.Mock(name="complete")
            with mock.patch.object(self.catcher, "complete", fake_complete):
                async with self.catcher:
                    self.info["result"] = result
                    self.assertEqual(len(fake_complete.mock_calls), 0)

            fake_complete.assert_called_once_with(result, status=200)

        async it "completes with a message from the exception and default status of 500":
            msg = mock.Mock(name="msg")

            error = PhotonsAppError("lol")

            fake_complete = mock.Mock(name="complete")
            fake_message_from_exc = mock.Mock(name="message_from_exc", return_value=msg)

            with mock.patch.object(self.catcher, "complete", fake_complete):
                with mock.patch("photons_interactor.request_handlers.base.message_from_exc", fake_message_from_exc):
                    async with self.catcher:
                        self.assertEqual(len(fake_complete.mock_calls), 0)
                        self.assertEqual(len(fake_message_from_exc.mock_calls), 0)
                        raise error

            fake_complete.assert_called_once_with(msg, status=500, exc_info=(PhotonsAppError, error, ATraceback()))
            fake_message_from_exc.assert_called_once_with(error)

        describe "message_from_exc":
            async it "returns exc.as_dict if result has error and status":
                error_message = str(uuid.uuid1())
                status = str(uuid.uuid1())

                class MyError:
                    def as_dict(self):
                        return {"error": error_message, "status": status}

                result = message_from_exc(MyError())
                self.assertEqual(result, {"error": error_message, "status": status})

            async it "returns internal server error if result if error or status not in result of exc.as_dict":
                error_message = str(uuid.uuid1())
                status = str(uuid.uuid1())

                class MyError:
                    def as_dict(self):
                        return {"error": error_message}

                result = message_from_exc(MyError())
                self.assertEqual(result, {"status": 500, "error": "Internal Server Error", "error_code": "InternalServerError"})

                class MyError2:
                    def as_dict(self):
                        return {"status": status}

                result = message_from_exc(MyError2())
                self.assertEqual(result, {"status": 500, "error": "Internal Server Error", "error_code": "InternalServerError"})

            async it "returns internal server error if exc has no as_dict":
                class MyError:
                    pass

                result = message_from_exc(MyError())
                self.assertEqual(result, {"status": 500, "error": "Internal Server Error", "error_code": "InternalServerError"})

            async it "returns kwargs if the error is a Finished":
                exc = Finished(status=408, reason="I'm a teapot")

                result = message_from_exc(exc)
                self.assertEqual(result, {"status": 408, "reason": "I'm a teapot"})

            async it "converts any other DelfickError into dict with status 400 and error as the exc.as_dict":
                class BadError(DelfickError):
                    pass
                exc = BadError(wat=1, blah=2)
                result = message_from_exc(exc)
                self.assertEqual(result, {"status": 400, "error": {"wat": 1, "blah": 2}, "error_code": "BadError"})

                exc = PhotonsAppError(other=3, meh=3)
                result = message_from_exc(exc)
                self.assertEqual(result, {"status": 400, "error": {"other": 3, "meh": 3}, "error_code": "PhotonsAppError"})

            async it "converts everything else into internal server error":
                exc = ValueError("WRONG!")
                result = message_from_exc(exc)
                self.assertEqual(result, {"status": 500, "error": "Internal Server Error", "error_code": "InternalServerError"})

        describe "complete":
            async before_each:
                self.exc_info = mock.Mock(name="exc_info")

            async it "calls send_msg with the msg if it's not a dictionary":
                kls = type("kls", (object, ), {})
                for thing in (0, 1, [], [1], True, False, None, lambda: 1, kls, kls()):
                    status = mock.Mock(name="status")
                    send_msg = mock.Mock(name="send_msg")
                    with mock.patch.object(self.catcher, "send_msg", send_msg):
                        self.catcher.complete(thing, status=status, exc_info=self.exc_info)
                    send_msg.assert_called_once_with(thing, status=status, exc_info=self.exc_info)

            async it "overrides status with what is found in the dict msg":
                status = mock.Mock(name="status")
                thing = {"status": 300}
                send_msg = mock.Mock(name="send_msg")
                with mock.patch.object(self.catcher, "send_msg", send_msg):
                    self.catcher.complete(thing, status=status)
                send_msg.assert_called_once_with(thing, status=300, exc_info=None)

            async it "reprs random objects":
                class Other:
                    def __repr__(self):
                        return "<<<OTHER>>>"

                thing = {"status": 301, "other": Other()}
                expected = {"status": 301, "other": "<<<OTHER>>>"}

                status = mock.Mock(name="status")
                send_msg = mock.Mock(name="send_msg")
                with mock.patch.object(self.catcher, "send_msg", send_msg):
                    self.catcher.complete(thing, status=status)
                send_msg.assert_called_once_with(expected, status=301, exc_info=None)

            async it "hexlifies bytes objects":
                val = str(uuid.uuid1()).replace("-", "")
                unhexlified = binascii.unhexlify(val)

                thing = {"status": 302, "thing": unhexlified}
                expected = {"status": 302, "thing": val}

                status = mock.Mock(name="status")
                send_msg = mock.Mock(name="send_msg")
                with mock.patch.object(self.catcher, "send_msg", send_msg):
                    self.catcher.complete(thing, status=status)
                send_msg.assert_called_once_with(expected, status=302, exc_info=None)

            async it "converts bitarrays into hexlified data":
                val = str(uuid.uuid1()).replace("-", "")
                unhexlified = binascii.unhexlify(val)

                b = bitarray.bitarray()
                b.frombytes(unhexlified)

                thing = {"status": 302, "thing": b}
                expected = {"status": 302, "thing": val}

                status = mock.Mock(name="status")
                send_msg = mock.Mock(name="send_msg")
                with mock.patch.object(self.catcher, "send_msg", send_msg):
                    self.catcher.complete(thing, status=status)
                send_msg.assert_called_once_with(expected, status=302, exc_info=None)

        describe "send_msg":
            async before_each:
                self.request = mock.Mock(name='request', spec=["_finished", "send_msg"])
                self.catcher = AsyncCatcher(self.request, self.info)
                self.exc_info = mock.Mock(name="exc_info")

            async it "does nothing if the request is already finished and ws_connection object":
                msg = mock.Mock(name="msg")
                self.request._finished = True
                self.catcher.send_msg(msg)
                self.assertEqual(len(self.request.send_msg.mock_calls), 0)

            async it "uses request.send_msg if final is None":
                msg = mock.Mock(name="msg")
                status = mock.Mock(name="status")
                self.request._finished = False
                self.catcher.final = None
                self.catcher.send_msg(msg, status=status, exc_info=self.exc_info)
                self.request.send_msg.assert_called_once_with(msg, status, exc_info=self.exc_info)

            async it "uses final if it was specified":
                msg = mock.Mock(name="msg")
                self.request._finished = False

                final = mock.Mock(name="final")
                self.catcher.final = final

                self.catcher.send_msg(msg, exc_info=self.exc_info)
                self.assertEqual(len(self.request.send_msg.mock_calls), 0)
                final.assert_called_once_with(msg, exc_info=self.exc_info)

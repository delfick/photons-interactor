# coding: spec

from photons_interactor.request_handlers.base import Simple

from tornado.testing import AsyncHTTPTestCase
from unittest import mock
import tornado
import types
import uuid
import json
import sys

describe AsyncHTTPTestCase, "RequestsMixin":
    def assertResponse(self, response, expected):
        self.assertEqual(json.loads(response.body.decode()), expected)

    describe "body as json":
        def get_app(self):
            self.path = "/blah"

            class Handler(Simple):
                async def do_post(s):
                    return str(s.body_as_json())
            return tornado.web.Application([(self.path, Handler)])

        it "complains if the body is empty":
            response = self.fetch(self.path, body="", method="POST")
            self.assertEqual(response.code, 400)
            self.assertResponse(response, {"reason": "Failed to load body as json", "error": mock.ANY, "status": 400})

        it "complains if the body is not valid json":
            response = self.fetch(self.path, body="{", method="POST")
            self.assertEqual(response.code, 400)
            self.assertResponse(response, {"reason": "Failed to load body as json", "error": mock.ANY, "status": 400})

        it "returns as a dictionary if valid":
            body = {"one": "two", "three": None, "four": [1, 2]}
            response = self.fetch(self.path, body=json.dumps(body), method="POST")
            self.assertEqual(response.code, 200)
            self.assertEqual(response.body, str(body).encode())

    describe "send_msg":
        def get_app(self):
            self.path = "/blah"
            self.replies = []

            class Handler(Simple):
                def process_reply(s, msg, exc_info=None):
                    return self.replies.append((msg, exc_info))

                async def do_post(s):
                    body = s.body_as_json()
                    kwargs = {}
                    if "msg" in body:
                        kwargs = {"msg": body["msg"]}
                    elif "error" in body:
                        try:
                            raise ValueError(body["error"])
                        except ValueError as error:
                            kwargs["msg"] = {"error": "error"}
                            kwargs["exc_info"] = sys.exc_info()
                    else:
                        class Thing:
                            def as_dict(s2):
                                return {"blah": "meh"}
                        kwargs["msg"] = Thing()

                    if 'status' in body:
                        kwargs["status"] = body["status"]

                    s.send_msg(**kwargs)
            return tornado.web.Application([(self.path, Handler)])

        it "calls as_dict on the message if it has that":
            response = self.fetch(self.path, method="POST", body="{}")
            self.assertEqual(response.code, 200)
            self.assertResponse(response, {"blah": "meh"})
            self.assertEqual(response.headers.get("Content-Type"), 'application/json; charset=UTF-8')

        it "is application/json if a list":
            body = {"msg": [1, 2, 3]}
            response = self.fetch(self.path, method="POST", body=json.dumps(body))
            self.assertEqual(response.code, 200)
            self.assertResponse(response, [1, 2, 3])
            self.assertEqual(response.headers.get("Content-Type"), 'application/json; charset=UTF-8')

        it "overrides status with what is in the msg":
            body = {"msg": {"status": 400, "tree": "branch"}}
            response = self.fetch(self.path, method="POST", body=json.dumps(body))
            self.assertEqual(response.code, 400)
            self.assertResponse(response, {"status": 400, "tree": "branch"})
            self.assertEqual(response.headers.get("Content-Type"), 'application/json; charset=UTF-8')

            body = {"msg": {"status": 400, "tree": "branch"}, "status": 500}
            response = self.fetch(self.path, method="POST", body=json.dumps(body))
            self.assertEqual(response.code, 400)
            self.assertResponse(response, {"status": 400, "tree": "branch"})
            self.assertEqual(response.headers.get("Content-Type"), 'application/json; charset=UTF-8')

        it "uses status passed in if no status in msg":
            body = {"msg": {"tree": "branch"}, "status": 501}
            response = self.fetch(self.path, method="POST", body=json.dumps(body))
            self.assertEqual(response.code, 501)
            self.assertResponse(response, {"tree": "branch"})
            self.assertEqual(response.headers.get("Content-Type"), 'application/json; charset=UTF-8')

        it "empty body if msg is None":
            body = {"msg": None}
            response = self.fetch(self.path, method="POST", body=json.dumps(body))
            self.assertEqual(response.code, 200)
            self.assertEqual(response.body, b"")

        it "treats html as html":
            msg = "<html><body/></html>"
            body = {"msg": msg}
            response = self.fetch(self.path, method="POST", body=json.dumps(body))
            self.assertEqual(response.code, 200)
            self.assertEqual(response.body, msg.encode())
            self.assertEqual(response.headers.get("Content-Type"), 'text/html; charset=UTF-8')

            msg = "<!DOCTYPE html><html><body/></html>"
            body = {"msg": msg}
            response = self.fetch(self.path, method="POST", body=json.dumps(body))
            self.assertEqual(response.code, 200)
            self.assertEqual(response.body, msg.encode())
            self.assertEqual(response.headers.get("Content-Type"), 'text/html; charset=UTF-8')

            body = {"msg": msg, "status": 500}
            response = self.fetch(self.path, method="POST", body=json.dumps(body))
            self.assertEqual(response.code, 500)
            self.assertEqual(response.body, msg.encode())
            self.assertEqual(response.headers.get("Content-Type"), 'text/html; charset=UTF-8')

        it "treats string as text/plain":
            msg = str(uuid.uuid1())
            body = {"msg": msg}
            response = self.fetch(self.path, method="POST", body=json.dumps(body))
            self.assertEqual(response.code, 200)
            self.assertEqual(response.body, msg.encode())
            self.assertEqual(response.headers.get("Content-Type"), 'text/plain; charset=UTF-8')

            body = {"msg": msg, "status": 403}
            response = self.fetch(self.path, method="POST", body=json.dumps(body))
            self.assertEqual(response.code, 403)
            self.assertEqual(response.body, msg.encode())
            self.assertEqual(response.headers.get("Content-Type"), 'text/plain; charset=UTF-8')

        it "processes replies":
            self.fetch(self.path, method="POST", body=json.dumps({"msg": "one"}))
            self.assertEqual(self.replies.pop(0), ("one", None))

            class ATraceback:
                def __eq__(self, other):
                    return isinstance(other, types.TracebackType)

            class AValueError:
                def __init__(self, msg):
                    self.msg = msg

                def __eq__(self, other):
                    return isinstance(other, ValueError) and str(other) == self.msg

            self.fetch(self.path, method="POST", body=json.dumps({"error": "wat"}))
            self.assertEqual(self.replies.pop(0)
                , ({"error": "error"}, (ValueError, AValueError("wat"), ATraceback()))
                )

            # Make sure we got all of them
            self.assertEqual(self.replies, [])

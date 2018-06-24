# coding: spec

from photons_interactor.request_handlers.base import Simple, Finished

from tornado.testing import AsyncHTTPTestCase
import tornado
import asyncio
import uuid
import json

describe AsyncHTTPTestCase, "Simple without error":
    describe "With no methods":
        def get_app(self):
            return tornado.web.Application([("/", Simple)])

        it "gets method not supported for all the methods":
            for method, body in (("GET", None), ("POST", b''), ("PUT", b''), ("DELETE", None), ("PATCH", b'')):
                if body is None:
                    response = self.fetch("/", method=method)
                else:
                    response = self.fetch("/", method=method, body=body)

            self.assertEqual(response.code, 405)

    describe "With Get":
        def get_app(self):
            self.path = "/info/blah/one/two"
            self.result = str(uuid.uuid1())

            class FilledSimple(Simple):
                async def do_get(s, *, one, two):
                    self.assertEqual(one, "one")
                    self.assertEqual(two, "two")
                    self.assertEqual(s.request.path, "/info/blah/one/two")
                    return self.result
            return tornado.web.Application([("/info/blah/(?P<one>.*)/(?P<two>.*)", FilledSimple)])

        it "allows GET requests":
            response = self.fetch(self.path)
            self.assertEqual(response.code, 200)
            self.assertEqual(response.body, self.result.encode())

    describe "With Post":
        def get_app(self):
            self.path = "/info/blah/one/two"
            self.body = str(uuid.uuid1())
            self.result = str(uuid.uuid1())

            class FilledSimple(Simple):
                async def do_post(s, one, two):
                    self.assertEqual(one, "one")
                    self.assertEqual(two, "two")
                    self.assertEqual(s.request.path, "/info/blah/one/two")
                    self.assertEqual(s.request.body, self.body.encode())
                    return self.result
            return tornado.web.Application([("/info/blah/(.*)/(.*)", FilledSimple)])

        it "allows POST requests":
            response = self.fetch(self.path, method="POST", body=self.body)
            self.assertEqual(response.code, 200)
            self.assertEqual(response.body, self.result.encode())

    describe "With Put":
        def get_app(self):
            self.path = "/info/blah/one/two"
            self.body = str(uuid.uuid1())
            self.result = str(uuid.uuid1())

            class FilledSimple(Simple):
                async def do_put(s, *, one, two):
                    self.assertEqual(one, "one")
                    self.assertEqual(two, "two")
                    self.assertEqual(s.request.path, "/info/blah/one/two")
                    self.assertEqual(s.request.body, self.body.encode())
                    return self.result
            return tornado.web.Application([("/info/blah/(?P<one>.*)/(?P<two>.*)", FilledSimple)])

        it "allows PUT requests":
            response = self.fetch(self.path, method="PUT", body=self.body)
            self.assertEqual(response.code, 200)
            self.assertEqual(response.body, self.result.encode())

    describe "With Patch":
        def get_app(self):
            self.path = "/info/blah/one/two"
            self.body = str(uuid.uuid1())
            self.result = str(uuid.uuid1())

            class FilledSimple(Simple):
                async def do_patch(s, one, two):
                    self.assertEqual(one, "one")
                    self.assertEqual(two, "two")
                    self.assertEqual(s.request.path, "/info/blah/one/two")
                    self.assertEqual(s.request.body, self.body.encode())
                    return self.result
            return tornado.web.Application([("/info/blah/(.*)/(.*)", FilledSimple)])

        it "allows PATCH requests":
            response = self.fetch(self.path, method="PATCH", body=self.body)
            self.assertEqual(response.code, 200)
            self.assertEqual(response.body, self.result.encode())

    describe "With Delete":
        def get_app(self):
            self.path = "/info/blah/one/two"
            self.result = str(uuid.uuid1())

            class FilledSimple(Simple):
                async def do_delete(s, *, one, two):
                    self.assertEqual(one, "one")
                    self.assertEqual(two, "two")
                    self.assertEqual(s.request.path, "/info/blah/one/two")
                    return self.result
            return tornado.web.Application([("/info/blah/(?P<one>.*)/(?P<two>.*)", FilledSimple)])

        it "allows DELETE requests":
            response = self.fetch(self.path, method="DELETE")
            self.assertEqual(response.code, 200)
            self.assertEqual(response.body, self.result.encode())

# This is so the send_msg logic in AsyncCatcher works
describe AsyncHTTPTestCase, "no ws_connection object":
    def get_app(self):
        self.path = "/info/blah"
        self.f = asyncio.Future()

        class FilledSimple(Simple):
            async def do_get(s):
                s.send_msg({"other": "stuff"})
                assert not hasattr(s, "ws_connection")
                self.f.set_result(True)
                return {"thing": "blah"}
        return tornado.web.Application([(self.path, FilledSimple)])

    it "ha no ws_connection":
        response = self.fetch(self.path)
        self.assertEqual(json.loads(response.body.decode()), {"other": "stuff"})
        assert self.f.done()

describe AsyncHTTPTestCase, "Simple with error":
    def assert_correct_response(self, response, status, body):
        self.assertEqual(response.code, status)
        self.assertEqual(json.dumps(body, sort_keys=True), json.dumps(json.loads(response.body.decode()), sort_keys=True))
        self.assertEqual(response.headers["Content-Type"], 'application/json; charset=UTF-8')

    describe "With Get":
        def get_app(self):
            self.path = "/info/blah"
            self.reason = str(uuid.uuid1())

            class FilledSimple(Simple):
                async def do_get(s):
                    self.assertEqual(s.request.path, "/info/blah")
                    raise Finished(status=501, reason=self.reason)
            return tornado.web.Application([(self.path, FilledSimple)])

        it "allows GET requests":
            response = self.fetch(self.path)
            self.assert_correct_response(response
                , status = 501
                , body = {"status": 501, "reason": self.reason}
                )

    describe "With Post":
        def get_app(self):
            self.path = "/info/blah"
            self.body = str(uuid.uuid1())
            self.reason = str(uuid.uuid1())

            class FilledSimple(Simple):
                async def do_post(s):
                    self.assertEqual(s.request.path, "/info/blah")
                    self.assertEqual(s.request.body, self.body.encode())
                    raise Finished(status=501, reason=self.reason)
            return tornado.web.Application([(self.path, FilledSimple)])

        it "allows POST requests":
            response = self.fetch(self.path, method="POST", body=self.body)
            self.assert_correct_response(response
                , status = 501
                , body = {"status": 501, "reason": self.reason}
                )

    describe "With Put":
        def get_app(self):
            self.path = "/info/blah"
            self.body = str(uuid.uuid1())
            self.reason = str(uuid.uuid1())

            class FilledSimple(Simple):
                async def do_put(s):
                    self.assertEqual(s.request.path, "/info/blah")
                    self.assertEqual(s.request.body, self.body.encode())
                    raise Finished(status=501, reason=self.reason)
            return tornado.web.Application([(self.path, FilledSimple)])

        it "allows PUT requests":
            response = self.fetch(self.path, method="PUT", body=self.body)
            self.assert_correct_response(response
                , status = 501
                , body = {"status": 501, "reason": self.reason}
                )

    describe "With Patch":
        def get_app(self):
            self.path = "/info/blah"
            self.body = str(uuid.uuid1())
            self.reason = str(uuid.uuid1())

            class FilledSimple(Simple):
                async def do_patch(s):
                    self.assertEqual(s.request.path, "/info/blah")
                    self.assertEqual(s.request.body, self.body.encode())
                    raise Finished(status=501, reason=self.reason)
            return tornado.web.Application([(self.path, FilledSimple)])

        it "allows PATCH requests":
            response = self.fetch(self.path, method="PATCH", body=self.body)
            self.assert_correct_response(response
                , status = 501
                , body = {"status": 501, "reason": self.reason}
                )

    describe "With Delete":
        def get_app(self):
            self.path = "/info/blah"
            self.reason = str(uuid.uuid1())

            class FilledSimple(Simple):
                 async def do_delete(s):
                    self.assertEqual(s.request.path, "/info/blah")
                    raise Finished(status=501, reason=self.reason)
            return tornado.web.Application([(self.path, FilledSimple)])

        it "allows DELETE requests":
            response = self.fetch(self.path, method="DELETE")
            self.assert_correct_response(response
                , status = 501
                , body = {"status": 501, "reason": self.reason}
                )

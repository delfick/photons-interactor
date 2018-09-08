from photons_interactor.errors import InteractorError

from photons_app import helpers as hp

from tornado.web import RequestHandler, HTTPError
from input_algorithms import spec_base as sb
from input_algorithms.dictobj import dictobj
from input_algorithms.meta import Meta
from delfick_error import DelfickError
from tornado import websocket
from bitarray import bitarray
import binascii
import logging
import json
import uuid

log = logging.getLogger("photons_interactor.request_handlers.base")

class Finished(InteractorError):
    pass

class InvalidMessage(InteractorError):
    pass

def reprer(o):
    if type(o) is bytes:
        return binascii.hexlify(o).decode()
    elif type(o) is bitarray:
        return binascii.hexlify(o.tobytes()).decode()
    return repr(o)

def message_from_exc(exc):
    as_dct = None

    if hasattr(exc, "as_dict") and as_dct is None:
        as_dct = exc.as_dict()
        if "error" in as_dct and "status" in as_dct:
            return as_dct

    if isinstance(exc, Finished):
        return exc.kwargs
    elif isinstance(exc, DelfickError):
        return {"status": 400, "error": as_dct, "error_code": exc.__class__.__name__}
    else:
        return {"status": 500, "error": "Internal Server Error", "error_code": "InternalServerError"}

class AsyncCatcher(object):
    def __init__(self, request, info, final=None):
        self.info = info
        self.final = final
        self.request = request

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        if exc is None:
            self.complete(self.info.get("result"), status=200)
            return

        exc.__traceback__ = tb
        if not isinstance(exc, DelfickError):
            log.exception(exc)
        elif not hasattr(exc, "_do_not_log"):
            log.error(exc)

        msg = message_from_exc(exc)
        self.complete(msg, status=500, exc_info=(exc_type, exc, tb))

        # And don't reraise the exception
        return True

    def send_msg(self, msg, status=200, exc_info=None):
        if self.request._finished and not hasattr(self.request, "ws_connection"):
            if type(msg) is dict:
                msg = json.dumps(msg, default=reprer, sort_keys=True, indent="    ")
                log.warning(hp.lc("Request already finished!", would_have_sent=msg))
            return

        if hasattr(msg, "exc_info") and exc_info is None:
            exc_info = msg.exc_info

        if self.final is None:
            self.request.send_msg(msg, status, exc_info=exc_info)
        else:
            self.final(msg, exc_info=exc_info)

    def complete(self, msg, status=200, exc_info=None):
        if type(msg) is dict:
            result = json.loads(json.dumps(msg, default=reprer, indent="    "))
        else:
            result = msg

        if type(result) is dict:
            status = result.get("status", status)

        self.send_msg(result, status=status, exc_info=exc_info)

class RequestsMixin:
    """
    A mixin class you may use for your handler which provides some handy methods
    for dealing with data
    """
    def async_catcher(self, info, final=None):
        return AsyncCatcher(self, info, final=final)

    def body_as_json(self, body=None):
        """Return the body of the request as a json object"""
        if body is None:
            body = self.request.body.decode()

        try:
            if type(body) is str:
                body = json.loads(body)
        except (TypeError, ValueError) as error:
            log.error("Failed to load body as json\t%s", body)
            raise Finished(status=400, reason="Failed to load body as json", error=error)

        return body

    def send_msg(self, msg, status=200, exc_info=None):
        """
        This determines what content-type and exact body to write to the response

        If ``msg`` has ``as_dict``, we call it.

        If ``msg`` is a dictionary and has status, we use that as the status of
        the request, otherwise we say it's a 200.

        If there is ``html`` in ``msg``, we use that as the body of the request.

        If ``msg`` is None, we close without a body.

        * If ``msg`` is a ``dict`` or ``list``, we write it as a json object.
        * If ``msg`` starts with ``<html>`` or ``<!DOCTYPE html>`` we treat it
          as html content
        * Otherwise we write ``msg`` as ``text/plain``
        """
        if hasattr(msg, "exc_info") and exc_info is None:
            exc_info = msg.exc_info

        if hasattr(msg, "as_dict"):
            msg = msg.as_dict()

        if type(msg) is dict:
            status = msg.get("status", status)
        self.set_status(status)

        if type(msg) is dict and "html" in msg:
            msg = msg["html"]

        if msg is None:
            self.finish()
            return

        if type(msg) in (dict, list):
            self.set_header("Content-Type", 'application/json; charset=UTF-8')
            self.write(json.dumps(msg, default=reprer, sort_keys=True, indent="    "))
        elif msg.lstrip().startswith("<html>") or msg.lstrip().startswith("<!DOCTYPE html>"):
            self.write(msg)
        else:
            self.set_header("Content-Type", 'text/plain; charset=UTF-8')
            self.write(msg)
        self.finish()

class Simple(RequestsMixin, RequestHandler):
    """
    Helper for using ``self.async_catcher`` from ``RequestsMixin`` for most HTTP verbs.

    .. code-block:: python

        class MyRequestHandler(Simple):
            async def do_get():
                return "<html><body><p>lol</p></body></html>"

    Essentially you define ``async def do_<verb>(self)`` methods for each verb
    you want to support.

    This supports

    * get
    * put
    * post
    * patch
    * delete
    """

    async def get(self, *args, **kwargs):
        if not hasattr(self, "do_get"):
            raise HTTPError(405)

        info = {"result": None}
        async with self.async_catcher(info):
            info["result"] = await self.do_get(*args, **kwargs)

    async def put(self, *args, **kwargs):
        if not hasattr(self, "do_put"):
            raise HTTPError(405)

        info = {"result": None}
        async with self.async_catcher(info):
            info["result"] = await self.do_put(*args, **kwargs)

    async def post(self, *args, **kwargs):
        if not hasattr(self, "do_post"):
            raise HTTPError(405)

        info = {"result": None}
        async with self.async_catcher(info):
            info["result"] = await self.do_post(*args, **kwargs)

    async def patch(self, *args, **kwargs):
        if not hasattr(self, "do_patch"):
            raise HTTPError(405)

        info = {"result": None}
        async with self.async_catcher(info):
            info["result"] = await self.do_patch(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        if not hasattr(self, "do_delete"):
            raise HTTPError(405)

        info = {"result": None}
        async with self.async_catcher(info):
            info["result"] = await self.do_delete(*args, **kwargs)

json_spec = sb.match_spec(
      (bool, sb.any_spec())
    , (int, sb.any_spec())
    , (float, sb.any_spec())
    , (str, sb.any_spec())
    , (list, lambda: sb.listof(json_spec))
    , (type(None), sb.any_spec())
    , fallback=lambda: sb.dictof(sb.string_spec(), json_spec)
    )

wsconnections = {}

class SimpleWebSocketBase(RequestsMixin, websocket.WebSocketHandler):
    """
    Used for websocket handlers

    Implement ``process_message``

    .. automethod:: photons_interactor.request_handlers.base.SimpleWebSocketBase.process_message

    This class takes in messages of the form ``{"path": <string>, "message_id": <string>, "body": <dictionary}``

    It will respond with messages of the form ``{"reply": <reply>, "message_id": <message_id>}``

    It treats path of ``__tick__`` as special and respond with ``{"reply": {"ok": "thankyou"}, "message_id": "__tick__"}``

    It relies on the client side closing the connection when it's finished.
    """
    def initialize(self, server_time):
        self.server_time = server_time

    class WSMessage(dictobj.Spec):
        path = dictobj.Field(sb.string_spec, wrapper=sb.required)
        message_id = dictobj.Field(sb.string_spec, wrapper=sb.required)
        body = dictobj.Field(json_spec, wrapper=sb.required)

    message_spec = WSMessage.FieldSpec()

    class Closing(object):
        pass

    def open(self):
        self.key = str(uuid.uuid1())
        log.info(hp.lc("WebSocket opened", key=self.key))
        self.reply(self.server_time, message_id="__server_time__")

    def reply(self, msg, message_id=None, exc_info=None):
        # I bypass tornado converting the dictionary so that non jsonable things can be repr'd
        if hasattr(msg, "as_dict"):
            msg = msg.as_dict()
        reply = {"reply": msg, "message_id": message_id}
        reply = json.dumps(reply, default=lambda o: repr(o)).replace("</", "<\\/")

        if self.ws_connection:
            self.write_message(reply)

    def on_message(self, message):
        log.debug(hp.lc("websocket message", message=message, key=self.key))
        try:
            parsed = json.loads(message)
        except (TypeError, ValueError) as error:
            self.reply({"error": "Message wasn't valid json\t{0}".format(str(error))})
            return

        if type(parsed) is dict and "path" in parsed and parsed["path"] == "__tick__":
            parsed["message_id"] = "__tick__"
            parsed["body"] = "__tick__"

        try:
            msg = self.message_spec.normalise(Meta.empty(), parsed)
        except Exception as error:
            log.exception(hp.lc("Invalid message received on websocket", error=error, got=parsed))
            if hasattr(error, "as_dict"):
                error = error.as_dict()
            else:
                error = str(error)

            self.reply({"error": InvalidMessage(error=error).as_dict()})
        else:
            path = msg.path
            body = msg.body
            message_id = msg.message_id

            if path == "__tick__":
                self.reply({"ok": "thankyou"}, message_id=message_id)
                return

            def on_processed(msg, exc_info=None):
                if msg is self.Closing:
                    self.reply({"closing": "goodbye"}, message_id=message_id)
                    self.close()
                    return

                self.reply(msg, message_id=message_id, exc_info=exc_info)

            async def doit():
                info = {}

                progress_cb = lambda progress: self.reply({"progress": progress}, message_id=message_id)
                async with self.async_catcher(info, on_processed):
                    info["result"] = await self.process_message(path, body, message_id, progress_cb)

            def done(*args):
                if self.key in wsconnections:
                    del wsconnections[self.key]

            t = hp.async_as_background(doit())
            t.add_done_callback(done)
            wsconnections[self.key] = t

    async def process_message(self, path, body, message_id, progress_cb):
        """
        Return the response to be sent back when we get a message from the conn.

        path
            The uri specified in the message

        body
            The body specified in the message

        message_id
            The unique message_id for this stream of requests as supplied in the request

        progress_cb
            A callback that will send a message of the form ``{"progress": <progress>, "message_id": <message_id}``
            where ``<progress>`` is the argument passed into the callback
        """
        raise NotImplementedError

    def on_close(self):
        """Hook for when a websocket connection closes"""
        log.info(hp.lc("WebSocket closed", key=self.key))

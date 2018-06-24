from photons_interactor.errors import InteractorError

from photons_app import helpers as hp

from tornado.web import RequestHandler, HTTPError
from delfick_error import DelfickError
from bitarray import bitarray
import binascii
import logging
import json

log = logging.getLogger("photons_interactor.request_handlers.base")

class Finished(InteractorError):
    pass

def reprer(o):
    if type(o) is bytes:
        return binascii.hexlify(o).decode()
    elif type(o) is bitarray:
        return binascii.hexlify(o.tobytes()).decode()
    return repr(o)

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

        msg = self.message_from_exc(exc)
        self.complete(msg, status=500)

        # And don't reraise the exception
        return True

    def message_from_exc(self, exc):
        as_dct = None

        if hasattr(exc, "as_dict") and as_dct is None:
            as_dct = exc.as_dict()
            if "error" in as_dct and "status" in as_dct:
                return as_dct

        if isinstance(exc, Finished):
            return exc.kwargs
        elif isinstance(exc, DelfickError):
            return {"status": 400, "error": as_dct}
        else:
            return {"status": 500, "error": "Internal Server Error"}

    def send_msg(self, msg, status=200):
        if self.request._finished and not hasattr(self.request, "ws_connection"):
            if type(msg) is dict:
                msg = json.dumps(msg, default=reprer, sort_keys=True, indent="    ")
                log.warning(hp.lc("Request already finished!", would_have_sent=msg))
            return

        if self.final is None:
            self.request.send_msg(msg, status)
        else:
            self.final(msg)

    def complete(self, msg, status=200):
        if type(msg) is dict:
            result = json.loads(json.dumps(msg, default=reprer, indent="    "))
        else:
            result = msg

        if type(result) is dict:
            status = result.get("status", status)

        self.send_msg(result, status=status)

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

    def send_msg(self, msg, status=200):
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

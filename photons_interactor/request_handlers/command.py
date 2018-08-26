from photons_interactor.request_handlers.base import Simple, SimpleWebSocketBase, Finished

from photons_app import helpers as hp
import logging
import inspect

def progress(body, logger_name, message, **kwargs):
    command_name = "Command"
    if body and type(body) is dict and "command" in body:
        command_name = body["command"]

    info = {}

    if isinstance(message, Exception):
        info["error_code"] =  message.__class__.__name__
        if hasattr(message, "as_dict"):
            info["error"] = message.as_dict()
        else:
            info["error"] = str(message)
    else:
        info["info"] = message

    info.update(kwargs)

    if "error" in info:
        logging.getLogger(logger_name).error(hp.lc(f"{command_name} progress", **info))
    else:
        logging.getLogger(logger_name).info(hp.lc(f"{command_name} progress", **info))

    return info

class CommandHandler(Simple):
    def initialize(self, commander):
        self.commander = commander

    async def do_put(self):
        j = self.body_as_json()

        def progress_cb(message, **kwargs):
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            progress(j, mod.__name__, message, **kwargs)

        return await self.commander.execute(j, progress_cb)

class WSHandler(SimpleWebSocketBase):
    def initialize(self, commander):
        self.commander = commander

    async def process_message(self, path, body, message_id, progress_cb):
        def cb(message, **kwargs):
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            info = progress(body, mod.__name__, message, **kwargs)
            progress_cb(info)

        if path == "/v1/lifx/command":
            return await self.commander.execute(body, cb)
        else:
            raise Finished(status=404, error=f"Specified path is invalid: {path}")

from photons_interactor.request_handlers.base import Simple, SimpleWebSocketBase, Finished

from photons_app import helpers as hp

import logging
import inspect

log = logging.getLogger("photons_interactor.request_handlers.command")

def progress(body, logger_name, message, do_log=True, **kwargs):
    command_name = "Command"
    if body and type(body) is dict and "command" in body:
        command_name = body["command"]

    info = {}

    if isinstance(message, Exception):
        info["error_code"] = message.__class__.__name__
        if hasattr(message, "as_dict"):
            info["error"] = message.as_dict()
        else:
            info["error"] = str(message)
    elif message is None:
        info["done"] = True
    else:
        info["info"] = message

    info.update(kwargs)

    if do_log:
        if "error" in info:
            logging.getLogger(logger_name).error(hp.lc(f"{command_name} progress", **info))
        else:
            logging.getLogger(logger_name).info(hp.lc(f"{command_name} progress", **info))

    return info

class ProcessReplyMixin:
    def process_reply(self, msg, exc_info=None):
        try:
            self.commander.process_reply(msg, exc_info)
        except KeyboardInterrupt:
            raise
        except Exception as error:
            log.exception(error)

class CommandHandler(Simple, ProcessReplyMixin):
    def initialize(self, commander):
        self.commander = commander

    async def do_put(self):
        j = self.body_as_json()

        def progress_cb(message, **kwargs):
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            info = progress(j, mod.__name__, message, **kwargs)
            self.process_reply(info)

        return await self.commander.execute(j, progress_cb, self)

class WSHandler(SimpleWebSocketBase, ProcessReplyMixin):
    def initialize(self, commander, server_time):
        self.commander = commander
        super().initialize(server_time)

    async def process_message(self, path, body, message_id, progress_cb):
        def cb(message, **kwargs):
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            info = progress(body, mod.__name__, message, **kwargs)
            progress_cb(info)

        if path == "/v1/lifx/command":
            return await self.commander.execute(body, cb, self)
        else:
            raise Finished(status=404, error=f"Specified path is invalid: {path}")

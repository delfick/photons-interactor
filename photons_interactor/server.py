from photons_interactor.request_handlers.command import CommandHandler
from photons_interactor.commander import Commander

from photons_device_finder import DeviceFinder

from tornado.httpserver import HTTPServer
import tornado.web
import tornado
import logging

log = logging.getLogger("photons_interactor.server")

class Server(object):
    def __init__(self, final_future, server_options, cleaners, target_register, protocol_register):
        self.cleaners = cleaners
        self.final_future = final_future
        self.server_options = server_options
        self.target_register = target_register
        self.protocol_register = protocol_register

    async def serve(self):
        await self.extra_futures()

        s = self.server_options

        http_server = HTTPServer(
              tornado.web.Application(
                  self.tornado_routes()
                , cookie_secret = s.cookie_secret
                )
            )

        log.info(f"Hosting server at http://{s.host}:{s.port}")

        http_server.listen(s.port, s.host)
        try:
            await self.final_future
        finally:
            http_server.stop()

    def tornado_routes(self):
        return [
              ( "/v1/lifx/command"
              , CommandHandler
              , {"commander": self.commander}
              )
            ]

    async def extra_futures(self):
        self.finder = DeviceFinder(self.target_register.resolve("lan")
            , repeat_spread = self.server_options.device_finder_repeat_spread
            )

        await self.finder.start()

        async def clean_finder():
            await self.finder.finish()
        self.cleaners.append(clean_finder)

        self.commander = Commander(self.finder, self.target_register, self.protocol_register)

from photons_interactor.request_handlers.command import CommandHandler, WSHandler
from photons_interactor.request_handlers.index import Index
from photons_interactor.commander import Commander

from photons_device_finder import DeviceFinder

from tornado.web import StaticFileHandler
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
            , ( "/v1/ws"
              , WSHandler
              , {"commander": self.commander}
              )
            , ( r"/static/(.*)"
              , StaticFileHandler
              , {"path": self.server_options.static_dest}
              )
            , ( self.server_options.html_path
              , Index
              )
            ]

    async def extra_futures(self):
        test_devices = None
        if self.server_options.fake_devices:
            from photons_interactor.commander import test_helpers as cthp
            test_devices = cthp.fake_devices(self.protocol_register)
            target = cthp.make_memory_target(self.final_future)

            runner = cthp.MemoryTargetRunner(target, test_devices["devices"])
            await runner.start()

            async def clean_memory_target():
                await runner.close()
            self.cleaners.append(clean_memory_target)
        else:
            target = self.target_register.resolve("lan")

        self.finder = DeviceFinder(target
            , **self.server_options.device_finder_options
            )

        await self.finder.start()

        async def clean_finder():
            await self.finder.finish()
        self.cleaners.append(clean_finder)

        self.commander = Commander(self.finder, self.target_register, self.protocol_register)

from photons_interactor.request_handlers.command import CommandHandler, WSHandler
from photons_interactor.request_handlers.base import wsconnections
from photons_interactor.request_handlers.index import Index
from photons_interactor.database.db_queue import DBQueue
from photons_interactor.commander import Commander

from photons_device_finder import DeviceFinder

from tornado.web import StaticFileHandler
from tornado.httpserver import HTTPServer
import tornado.web
import tornado
import logging
import time

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
              , {"commander": self.commander, "server_time": time.time()}
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

        self.db_queue = DBQueue(self.final_future, 5, lambda exc: 1, self.server_options.database.uri)
        self.cleaners.append(self.db_queue.finish)
        self.db_queue.start()

        self.finder = DeviceFinder(target
            , **self.server_options.device_finder_options
            )

        await self.finder.start()

        async def clean_finder():
            await self.finder.finish()
        self.cleaners.append(clean_finder)

        async def wait_for_ws():
            for t in list(wsconnections.values()):
                if not t.done():
                    try:
                        await t
                    except:
                        pass
        self.cleaners.append(wait_for_ws)

        self.commander = Commander(
              finder = self.finder
            , db_queue = self.db_queue
            , test_devices = test_devices
            , final_future = self.final_future
            , server_options = self.server_options
            , target_register = self.target_register
            , protocol_register = self.protocol_register
            )

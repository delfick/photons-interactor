from photons_interactor.request_handlers.command import CommandHandler, WSHandler
from photons_interactor.commander.commands.animations import AnimationsStore
from photons_interactor.commander.commands.tiles import ArrangeState
from photons_interactor.request_handlers.index import Index
from photons_interactor.database.db_queue import DBQueue

from photons_device_finder import DeviceFinder

from whirlwind.server import Server, wait_for_futures
from whirlwind.commander import Commander
from tornado.web import StaticFileHandler
import logging
import time

log = logging.getLogger("photons_interactor.server")


class Server(Server):
    def __init__(self, final_future, store=None):
        if store is None:
            from photons_interactor.commander.store import store, load_commands

            load_commands()

        self.store = store
        self.final_future = final_future
        self.wsconnections = {}

    def tornado_routes(self):
        return [
            ("/v1/lifx/command", CommandHandler, {"commander": self.commander}),
            (
                "/v1/ws",
                WSHandler,
                {
                    "commander": self.commander,
                    "server_time": time.time(),
                    "wsconnections": self.wsconnections,
                },
            ),
            (r"/static/(.*)", StaticFileHandler, {"path": self.server_options.static_dest}),
            (self.server_options.html_path, Index),
        ]

    async def setup(
        self, server_options, cleaners, target_register, protocol_register, animation_options
    ):
        self.cleaners = cleaners
        self.server_options = server_options
        self.target_register = target_register
        self.protocol_register = protocol_register

        test_devices = None
        if self.server_options.fake_devices:
            from photons_interactor.commander import test_helpers as cthp
            from photons_control import test_helpers as chp

            runner = chp.MemoryTargetRunner(self.final_future, cthp.fakery.devices)
            target = runner.target
            await runner.start()

            async def clean_memory_target():
                await runner.close()

            self.cleaners.append(clean_memory_target)
        else:
            target = self.target_register.resolve("lan")

        self.db_queue = DBQueue(
            self.final_future, 5, lambda exc: 1, self.server_options.database.uri
        )
        self.cleaners.append(self.db_queue.finish)
        self.db_queue.start()

        self.finder = DeviceFinder(target, **self.server_options.device_finder_options)

        self.arranger = ArrangeState()
        self.animations = AnimationsStore(
            self.server_options.animations_presets, self.arranger, animation_options
        )
        self.cleaners.append(self.animations.finish)

        await self.finder.start()

        async def clean_finder():
            await self.finder.finish()

        self.cleaners.append(clean_finder)

        # Make sure to wait for the wsconnections
        async def waiter():
            self.final_future.cancel()
            await wait_for_futures(self.wsconnections)

        self.cleaners.append(waiter)

        self.commander = Commander(
            self.store,
            finder=self.finder,
            db_queue=self.db_queue,
            arranger=self.arranger,
            animations=self.animations,
            test_devices=test_devices,
            final_future=self.final_future,
            server_options=self.server_options,
            target_register=self.target_register,
            protocol_register=self.protocol_register,
        )

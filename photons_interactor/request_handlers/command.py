from photons_interactor.request_handlers.base import Simple

class CommandHandler(Simple):
    def initialize(self, commander):
        self.commander = commander

    async def do_put(self):
        return await self.commander.execute(self.body_as_json())

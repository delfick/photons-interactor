from photons_interactor.request_handlers.base import Simple, SimpleWebSocketBase, Finished

class CommandHandler(Simple):
    def initialize(self, commander):
        self.commander = commander

    async def do_put(self):
        return await self.commander.execute(self.body_as_json())

class WSHandler(SimpleWebSocketBase):
    def initialize(self, commander):
        self.commander = commander

    async def process_message(self, path, body, message_id, progress_cb):
        if path == "/v1/lifx/command":
            return await self.commander.execute(body)
        else:
            raise Finished(status=404, error=f"Specified path is invalid: {path}")

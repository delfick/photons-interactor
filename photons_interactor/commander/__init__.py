from photons_interactor.commander.decorator import command_spec
from photons_interactor.commander.commands import Command

from option_merge import MergedOptions
from input_algorithms.meta import Meta

class Commander:
    def __init__(self, finder, target_register, protocol_register):
        self.command_spec = command_spec()

        self.meta = Meta(
              MergedOptions.using(
                { "finder": finder
                , "target_register": target_register
                , "protocol_register": protocol_register
                }
              )
            , []
            )

    async def execute(self, command):
        if not isinstance(command, Command):
            command = self.command_spec.normalise(self.meta.at("<input>"), command)
        return await command.execute()

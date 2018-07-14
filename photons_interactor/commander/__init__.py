from photons_interactor.commander.decorator import command_spec
from photons_interactor.commander.commands import Command

from option_merge import MergedOptions
from input_algorithms.meta import Meta

class Commander:
    """
    Entry point to commands.

    .. automethod:: photons_interactor.commander.Commander.execute
    """
    def __init__(self, finder, target_register, protocol_register, test_devices=None):
        self.command_spec = command_spec()

        self.meta = Meta(
              MergedOptions.using(
                { "finder": finder
                , "test_devices": test_devices
                , "target_register": target_register
                , "protocol_register": protocol_register
                }
              )
            , []
            )

    async def execute(self, command):
        """
        Responsible for creating a command and calling execute on it.

        If command is not already a Command instance then we normalise it
        into one and provide ``finder``, ``target_register`` and ``protocol_register``
        in the meta object.
        """
        if not isinstance(command, Command):
            command = self.command_spec.normalise(self.meta.at("<input>"), command)
        return await command.execute()

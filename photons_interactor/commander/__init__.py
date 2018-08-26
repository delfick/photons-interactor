from photons_interactor.commander.decorator import command_spec
from photons_interactor.commander.commands import Command

from input_algorithms.dictobj import dictobj
from option_merge import MergedOptions
from input_algorithms.meta import Meta
import asyncio

class Commander:
    """
    Entry point to commands.

    .. automethod:: photons_interactor.commander.Commander.execute
    """
    _merged_options_formattable = True

    def __init__(self, **options):
        self.command_spec = command_spec()

        everything = MergedOptions.using(
              options
            , {"commander": self}
            , dont_prefix = [dictobj]
            )

        self.meta = Meta(everything, [])

    async def execute(self, command, progress_cb, extra_options=None):
        """
        Responsible for creating a command and calling execute on it.

        If command is not already a Command instance then we normalise it
        into one.

        We have available on the meta object:

        __init__ options
            Anything that is provided to the Commander at __init__

        progress_cb
            A callback that takes in a message. This is provided by whatever
            calls execute. It should take a single variable.

        request_future
            A future that is cancelled after execute is finished

        extra options
            Anything provided as extra_options to this function
        """
        request_future = asyncio.Future()
        request_future._merged_options_formattable = True

        try:
            if not isinstance(command, Command):
                everything = MergedOptions.using(
                      self.meta.everything
                    , {"progress_cb": progress_cb, "request_future": request_future}
                    , extra_options or {}
                    , dont_prefix = [dictobj]
                    )

                meta = Meta(everything, self.meta.path).at("<input>")
                command = self.command_spec.normalise(meta, command)

            return await command.execute()
        finally:
            request_future.cancel()

from photons_interactor.commander import default_fields as df
from photons_interactor.commander.tiles import tile_dice
from photons_interactor.commander import helpers as chp
from photons_interactor.commander.store import store

from photons_messages import DeviceMessages

@store.command(name="tiles/dice")
class TileDiceCommand(store.Command):
    """
    Show dice on provided tiles and return the hsbk values that were sent
    """
    finder = store.injected("finder")
    target = store.injected("targets.lan")

    matcher = df.matcher_field
    refresh = df.refresh_field

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)

        result = chp.ResultBuilder()
        afr = await self.finder.args_for_run()
        reference = self.finder.find(filtr=fltr)

        await self.target.script(DeviceMessages.SetPower(level=65535)).run_with_all(reference, afr
            , error_catcher = result.error
            )

        result.result["results"]["tiles"] = await tile_dice(self.target, self.finder.find(filtr=fltr), afr
            , error_catcher = result.error
            )

        return result

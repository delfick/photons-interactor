from photons_interactor.commander import default_fields as df
from photons_interactor.commander.tiles import tile_dice
from photons_interactor.commander import helpers as chp
from photons_interactor.commander.store import store

@store.command(name="tiles/dice")
class TileDiceCommand(store.Command):
    """
    Show dice on provided tiles and return the hsbk values that were sent
    """
    finder = store.injected("finder")
    target = store.injected("targets.lan")

    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)

        result = chp.ResultBuilder()
        afr = await self.finder.args_for_run()
        result.result["results"]["tiles"] = await tile_dice(self.target, self.finder.find(filtr=fltr), afr, error_catcher=result.error)

        return result

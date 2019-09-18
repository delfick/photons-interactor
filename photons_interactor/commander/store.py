from photons_app.formatter import MergedOptionStringFormatter

from whirlwind.store import Store

store = Store(default_path="/v1/lifx/command", formatter=MergedOptionStringFormatter)


def load_commands():
    import photons_interactor.commander.commands  # noqa

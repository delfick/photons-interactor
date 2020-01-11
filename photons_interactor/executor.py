"""
Mainline to photons interactor

setup.py creates a `photons-interactor` shortcut that calls out to this file.
"""
from photons_interactor import VERSION

from photons_app.executor import App

from delfick_project.norms import sb
from textwrap import dedent
import argparse
import logging
import os

log = logging.getLogger("photons_interactor.executor")

cli_environment_defaults = App.cli_environment_defaults
other_cli_environment_defaults = {
    "INTERACTOR_HOST": ("--host", sb.NotSpecified),
    "INTERACTOR_PORT": ("--port", sb.NotSpecified),
    "LIFX_CONFIG": ("--config", "./interactor.yml"),
}
cli_environment_defaults.update(other_cli_environment_defaults)


class DefaultConfigFile(argparse.FileType):
    def __call__(self, location):
        if not os.path.exists(location):
            self.make_location(location)
        return super().__call__(location)

    def make_location(self, location):
        print(
            dedent(
                f"""
            Photons interactor needs a configuration file. This can be specified with
            the --config cli option or the LIFX_CONFIG environment variable.

            We tried looking at {location} but didn't see a config file.

            By pressing enter we will create a config file at {location} for you.

            Press ctrl-c to not go forward with this.
            """
            )
        )

        input()

        with open(location, "w") as fle:
            fle.write(
                dedent(
                    """
                ---

                interactor:
                  database:
                    uri: "sqlite:///{config_root}/interactor.db"
            """
                )
            )


class App(App):
    VERSION = VERSION
    cli_categories = ["photons_app", "interactor"]
    cli_description = "Interact with LIFX lights over the LAN"
    cli_environment_defaults = cli_environment_defaults

    def execute(self, args_obj, args_dict, extra_args, logging_handler):
        data = {
            "photons_app": {"use_uvloop": False, "addons": {"lifx.photons": "interactor"}},
            "interactor": dict(
                (k, v) for k, v in args_dict["interactor"].items() if v is not sb.NotSpecified
            ),
        }

        return super(App, self).execute(
            args_obj, args_dict, extra_args, logging_handler, extra_files=[data]
        )

    def specify_other_args(self, parser, defaults):
        parser = super(App, self).specify_other_args(parser, defaults)

        parser.add_argument(
            "--host",
            help="The host to put the server on",
            dest="interactor_host",
            **defaults["--host"],
        )

        parser.add_argument(
            "--port",
            help="The port to put the server on",
            dest="interactor_port",
            **defaults["--port"],
        )

        parser.add_argument(
            "--fake-devices",
            help="Use fake devices instead of the actual network",
            dest="interactor_fake_devices",
            action="store_true",
        )

        config_option = [p for p in parser._actions if "--config" in p.option_strings][0]
        config_option.type = DefaultConfigFile("r")

        return parser


main = App.main

if __name__ == "__main__":
    main()

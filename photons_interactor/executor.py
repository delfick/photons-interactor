"""
Mainline to photons interactor

setup.py creates a `photons-interactor` shortcut that calls out to this file.
"""
from photons_interactor import VERSION

from photons_app import helpers as hp
from photons_app.executor import App

from input_algorithms import spec_base as sb
from delfick_app import ArgumentError
from textwrap import dedent
import logging
import json
import sys

log = logging.getLogger("photons_interactor.executor")

cli_environment_defaults = App.cli_environment_defaults
other_cli_environment_defaults = {
      "INTERACTOR_HOST": ("--host", sb.NotSpecified)
    , "INTERACTOR_PORT": ("--port", sb.NotSpecified)
    , "LIFX_CONFIG": ("--config", "./interactor.yml")
    }
cli_environment_defaults.update(other_cli_environment_defaults)

class App(App):
    VERSION = VERSION
    cli_categories = ['photons_app', 'interactor']
    cli_description = "Interact with LIFX lights over the LAN"
    cli_environment_defaults = cli_environment_defaults

    def execute(self, args_obj, args_dict, extra_args, logging_handler):
        data = {
              "photons_app": { "addons": {"lifx.photons": "interactor"} }
            , "interactor": dict((k, v) for k, v in args_dict["interactor"].items() if v is not sb.NotSpecified)
            }

        with hp.a_temp_file() as fle:
            fle.write(json.dumps(data).encode())
            fle.flush()
            return super(App, self).execute(args_obj, args_dict, extra_args, logging_handler, extra_files=[fle.name])

    def specify_other_args(self, parser, defaults):
        parser = super(App, self).specify_other_args(parser, defaults)

        parser.add_argument("--host"
            , help = "The host to put the server on"
            , dest = "interactor_host"
            , **defaults["--host"]
            )

        parser.add_argument("--port"
            , help = "The port to put the server on"
            , dest = "interactor_port"
            , **defaults["--port"]
            )

        return parser

main = App.main
if __name__ == "__main__":
    main()

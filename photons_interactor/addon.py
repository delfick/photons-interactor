from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_app.formatter import MergedOptionStringFormatter
from photons_app.errors import PhotonsAppError
from photons_app.actions import an_action

from option_merge_addons import option_merge_addon_hook
from input_algorithms import spec_base as sb
from input_algorithms.meta import Meta
import pkg_resources
import subprocess
import shlex
import os

@option_merge_addon_hook(extras=[("lifx.photons", "__all__")])
def __lifx__(collector, *args, **kwargs):
    collector.register_converters(
          { (0, ("interactor", )): Options.FieldSpec(formatter=MergedOptionStringFormatter)
          }
        , Meta, collector.configuration, sb.NotSpecified
        )

@an_action()
async def serve(collector, **kwargs):
    conf = collector.configuration
    await Server(
          conf["photons_app"].final_future
        , conf["interactor"]
        , conf["photons_app"].cleaners
        , conf["target_register"]
        , conf["protocol_register"]
        ).serve()

@an_action()
async def npm(collector, reference, **kwargs):
    if not os.path.exists(pkg_resources.resource_filename("photons_interactor", "static/js")):
        raise PhotonsAppError("Npm commands are only available during development")

    extra = collector.configuration["photons_app"].extra
    assets = collector.configuration["interactor"].assets
    available = ["run", "install", "static", "watch", "test", "test:watch"]

    if reference in (None, "", sb.NotSpecified):
        raise PhotonsAppError("Please specify what command to run", available=available)

    assets.ensure_npm()

    try:
        if reference == "install":
            assets.run("install", *shlex.split(extra))
            return

        if reference == "run":
            assets.run(*shlex.split(extra))
            return

        if assets.needs_install:
            assets.run("install")

        elif reference == "static":
            assets.run("run-script", "build")

        elif reference == "watch":
            assets.run("run-script", "generate")

        elif reference == "test":
            assets.run("run-script", "test")

        elif reference == "test:watch":
            assets.run("run-script", "test:watch")

        else:
            raise PhotonsAppError("Didn't get a recognised command", want=reference, available=available)
    except subprocess.CalledProcessError as error:
        raise PhotonsAppError("Failed to run command", error=error)

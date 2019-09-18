from photons_interactor.database import database
from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_app.formatter import MergedOptionStringFormatter
from photons_app.errors import PhotonsAppError
from photons_app.actions import an_action
from photons_app import helpers as hp

from photons_transport.session.network import NetworkSession
from photons_transport.targets import LanTarget
from photons_messages import Services

from delfick_project.addons import addon_hook
from delfick_project.norms import sb
from functools import partial
import pkg_resources
import subprocess
import binascii
import logging
import asyncio
import shlex
import time
import os

log = logging.getLogger("photons_interactor.addon")


@addon_hook(extras=[("lifx.photons", "__all__")])
def __lifx__(collector, *args, **kwargs):
    collector.register_converters(
        {"interactor": Options.FieldSpec(formatter=MergedOptionStringFormatter)}
    )


@an_action(label="Interactor")
async def serve(collector, **kwargs):
    conf = collector.configuration
    await migrate(collector, extra="upgrade head")

    if "DISCOVERY_FILTER" in os.environ:
        serials = os.environ["DISCOVERY_FILTER"].split(",")

        class ModifiedNetworkSession(NetworkSession):
            async def add_service(s, serial, service, **kwargs):
                if serial in serials:
                    await super().add_service(serial, service, **kwargs)

            async def _do_search(s, *args, **kwargs):
                if serials[0] == ":":
                    found_now = set()
                    for serial in serials[1:]:
                        serial, ip = serial.split(":")
                        await super().add_service(serial, Services.UDP, port=56700, host=ip)
                        found_now.add(binascii.unhexlify(serial)[:6])
                    return list(found_now)
                else:
                    fn = await super()._do_search(*args, **kwargs)
                    return [s for s in fn if binascii.hexlify(s).decode() in serials]

        LanTarget.session_kls = ModifiedNetworkSession

    options = conf["interactor"]
    await Server(conf["photons_app"].final_future).serve(
        options.host,
        options.port,
        conf["interactor"],
        conf["photons_app"].cleaners,
        conf["target_register"],
        conf["protocol_register"],
    )


@an_action(label="Interactor")
async def migrate(collector, extra=None, **kwargs):
    """
    Migrate a database

    This task will use `Alembic <http://alembic.zzzcomputing.com>`_ to perform
    database migration tasks.

    Usage looks like:

    ``migrate -- revision --autogenerate  -m doing_some_change``

    Or

    ``migrate -- upgrade head``

    Basically, everything after the ``--`` is passed as commandline arguments
    to alembic.
    """
    if extra is None:
        extra = collector.configuration["photons_app"].extra
    await database.migrate(collector.configuration["interactor"].database, extra)


@an_action(label="Interactor")
async def npm(collector, reference, **kwargs):
    if not os.path.exists(pkg_resources.resource_filename("photons_interactor", "static/js")):
        raise PhotonsAppError("Npm commands are only available during development")

    extra = collector.configuration["photons_app"].extra
    assets = collector.configuration["interactor"].assets
    available = ["run", "install", "static", "watch", "test", "test:watch", "integration_test"]

    if reference in (None, "", sb.NotSpecified):
        raise PhotonsAppError("Please specify what command to run", available=available)

    assets.ensure_npm()

    async def cypress(typ):
        try:
            import asynctest  # noqa
        except ImportError:
            raise PhotonsAppError(
                'You must `pip install -e ".[tests]"` before you can run integration tests'
            )

        from whirlwind.test_helpers import free_port, port_connected

        port = free_port()
        env = {"CYPRESS_BASE_URL": f"http://127.0.0.1:{port}"}

        final_future = collector.configuration["photons_app"].final_future

        t = None
        try:
            collector.configuration["interactor"].host = "127.0.0.1"
            collector.configuration["interactor"].port = port
            collector.configuration["interactor"].fake_devices = True
            collector.configuration["interactor"].database.uri = "sqlite:///:memory:"

            t = hp.async_as_background(serve(collector))

            start = time.time()
            while time.time() - start < 5:
                if port_connected(port):
                    break
                await asyncio.sleep(0.01)

            if not port_connected(port):
                raise PhotonsAppError("Failed to start server for tests")

            loop = asyncio.get_event_loop()
            if os.environ.get("NO_BUILD_ASSETS") != "1":
                log.info("Building assets")
                await loop.run_in_executor(None, partial(assets.run, "run-script", "build"))

            log.info("Running cypress")
            await loop.run_in_executor(
                None, partial(assets.run, "run-script", f"cypress:{typ}", extra_env=env)
            )
        except Exception as error:
            if not final_future.done():
                final_future.set_exception(error)
        finally:
            if not final_future.done():
                final_future.set_result(None)
            if t:
                await t

    try:
        if reference == "install":
            assets.run("install", *shlex.split(extra))
            return

        if reference == "run":
            assets.run(*shlex.split(extra))
            return

        if assets.needs_install:
            assets.run("install")

        if reference == "static":
            assets.run("run-script", "build")

        elif reference == "watch":
            assets.run("run-script", "generate")

        elif reference == "test":
            assets.run("run-script", "test")

        elif reference == "integration_test:cli":
            await cypress("run")

        elif reference == "integration_test:ui":
            await cypress("open")

        elif reference == "test:watch":
            assets.run("run-script", "test:watch")

        else:
            raise PhotonsAppError(
                "Didn't get a recognised command", want=reference, available=available
            )
    except subprocess.CalledProcessError as error:
        raise PhotonsAppError("Failed to run command", error=error)

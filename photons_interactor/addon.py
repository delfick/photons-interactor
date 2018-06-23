from photons_interactor.options import Options
from photons_interactor.server import Server

from photons_app.formatter import MergedOptionStringFormatter
from photons_device_finder import DeviceFinder
from photons_app.actions import an_action

from option_merge_addons import option_merge_addon_hook
from input_algorithms import spec_base as sb
from input_algorithms.meta import Meta

@option_merge_addon_hook(extras=[("lifx.photons", "__all__")])
def __lifx__(collector, *args, **kwargs):
    DeviceFinder._merged_options_formattable = True
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

from photons_interactor.commander.commands.animations import presets_spec
from photons_interactor.database.database import Database
from photons_interactor.assets import Assets

from photons_app.formatter import MergedOptionStringFormatter

from delfick_project.norms import dictobj, sb
import secrets


class random_secret_spec(sb.string_spec):
    def normalise_empty(self, meta):
        return secrets.token_hex(32)


class Options(dictobj.Spec):
    host = dictobj.Field(
        sb.string_spec, default="localhost", help="The host to serve the server on"
    )

    port = dictobj.Field(sb.integer_spec, default=6100, help="The port to serve the server on")

    cookie_secret = dictobj.Field(
        random_secret_spec, help="The secret used to secure cookies in the web server"
    )

    device_finder_options = dictobj.Field(sb.dictionary_spec, help="Options for the device finder")

    assets = dictobj.Field(
        Assets.FieldSpec(formatter=MergedOptionStringFormatter),
        help="Options for where assets can be found",
    )

    animations_presets = dictobj.Field(
        presets_spec(), help="Presets for combinations of tile animations"
    )

    fake_devices = dictobj.Field(
        sb.boolean,
        default=False,
        help=""""
            Whether to look at the lan or use fake devices

            This is useful for integration tests
          """,
    )

    database = dictobj.Field(
        Database.FieldSpec(formatter=MergedOptionStringFormatter),
        wrapper=sb.required,
        help="Database options",
    )

    @property
    def static_dest(self):
        return self.assets.assets_folder

    @property
    def html_path(self):
        return "/(?:tiles.*)?"

from photons_interactor.assets import Assets

from photons_app.formatter import MergedOptionStringFormatter

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
import secrets

class random_secret_spec(sb.string_spec):
    def normalise_empty(self, meta):
        return secrets.token_hex(32)

class Options(dictobj.Spec):
    host = dictobj.Field(sb.string_spec, default="localhost"
        , help = "The host to serve the server on"
        )

    port = dictobj.Field(sb.integer_spec, default=6100
        , help = "The port to serve the server on"
        )

    cookie_secret = dictobj.Field(random_secret_spec
        , help = "The secret used to secure cookies in the web server"
        )

    device_finder_options = dictobj.Field(sb.dictionary_spec
        , help = "Options for the device finder"
        )

    assets = dictobj.Field(Assets.FieldSpec(formatter=MergedOptionStringFormatter)
        , help = "Options for where assets can be found"
        )

    @property
    def static_dest(self):
        return self.assets.assets_folder

    @property
    def html_path(self):
        return "/"

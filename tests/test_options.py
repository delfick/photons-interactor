# coding: spec

from photons_interactor import test_helpers as thp
from photons_interactor.options import Options

from photons_app.test_helpers import TestCase

from unittest import mock
import os

this_dir = os.path.dirname(__file__)
dist_dir = os.path.abspath(
    os.path.join(this_dir, "..", "photons_interactor", "static", "dist", "static")
)

describe TestCase, "Options":
    it "has defaults":
        options = thp.make_options(database={"uri": "somewhere"}, device_finder_options={})
        assert options.host == "localhost"
        assert options.port == 6100
        assert options.device_finder_options == {}

        cookie_secret = options.cookie_secret
        options2 = thp.make_options(database={"uri": "somewhere"})
        assert cookie_secret != options2.cookie_secret

        assert options.static_dest == dist_dir
        assert options.html_path == "/(?:tiles.*)?"
        assert options.database.as_dict() == {"uri": "somewhere", "db_migrations": mock.ANY}

    it "can set values of it's own":
        options = thp.make_options(
            "blah",
            9001,
            cookie_secret="meh",
            device_finder_options={"repeat_spread": 0.1},
            database={"uri": "somewhere"},
        )

        assert options.host == "blah"
        assert options.port == 9001
        assert options.cookie_secret == "meh"
        assert options.device_finder_options == {"repeat_spread": 0.1}
        assert options.database.as_dict() == {"uri": "somewhere", "db_migrations": mock.ANY}

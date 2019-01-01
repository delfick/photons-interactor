# coding: spec

from photons_interactor import test_helpers as thp
from photons_interactor.options import Options

from photons_app.test_helpers import TestCase

from unittest import mock
import os

this_dir = os.path.dirname(__file__)
dist_dir = os.path.abspath(os.path.join(this_dir, "..", "photons_interactor", "static", "dist", "static"))

describe TestCase, "Options":
    it "has defaults":
        options = thp.make_options(database={"uri": "somewhere"}, device_finder_options={})
        self.assertEqual(options.host, "localhost")
        self.assertEqual(options.port, 6100)
        self.assertEqual(options.device_finder_options, {})

        cookie_secret = options.cookie_secret
        options2 = thp.make_options(database={"uri": "somewhere"})
        self.assertNotEqual(cookie_secret, options2.cookie_secret)

        self.assertEqual(options.static_dest, dist_dir)
        self.assertEqual(options.html_path, "/(?:tiles.*)?")
        self.assertEqual(options.database.as_dict(), {"uri": "somewhere", "db_migrations": mock.ANY})

    it "can set values of it's own":
        options = thp.make_options("blah", 9001
            , cookie_secret="meh"
            , device_finder_options = {"repeat_spread": 0.1}
            , database = {"uri": "somewhere"}
            )

        self.assertEqual(options.host, "blah")
        self.assertEqual(options.port, 9001)
        self.assertEqual(options.cookie_secret, "meh")
        self.assertEqual(options.device_finder_options, {"repeat_spread": 0.1})
        self.assertEqual(options.database.as_dict(), {"uri": "somewhere", "db_migrations": mock.ANY})

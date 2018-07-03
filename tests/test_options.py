# coding: spec

from photons_interactor.options import Options

from photons_app.test_helpers import TestCase

import os

this_dir = os.path.dirname(__file__)
dist_dir = os.path.abspath(os.path.join(this_dir, "..", "photons_interactor", "static", "dist", "static"))

describe TestCase, "Options":
    it "has defaults":
        options = Options.FieldSpec().empty_normalise()
        self.assertEqual(options.host, "localhost")
        self.assertEqual(options.port, 6100)
        self.assertEqual(options.device_finder_options, {})

        cookie_secret = options.cookie_secret
        options2 = Options.FieldSpec().empty_normalise()
        self.assertNotEqual(cookie_secret, options2.cookie_secret)

        self.assertEqual(options.static_dest, dist_dir)
        self.assertEqual(options.html_path, "/")

    it "can set values of it's own":
        options = Options.FieldSpec().empty_normalise(
              host="blah"
            , port=9001
            , cookie_secret="meh"
            , device_finder_options = {"repeat_spread": 0.1}
            )

        self.assertEqual(options.host, "blah")
        self.assertEqual(options.port, 9001)
        self.assertEqual(options.cookie_secret, "meh")
        self.assertEqual(options.device_finder_options, {"repeat_spread": 0.1})

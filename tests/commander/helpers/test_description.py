# coding: spec

from photons_interactor.commander import default_fields as df
from photons_interactor.commander import helpers as chp

from photons_app.test_helpers import TestCase

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from textwrap import dedent

describe TestCase, "fields_description":
    it "only gets fields that have help specified":
        class Thing(dictobj.Spec):
            one = dictobj.Field(sb.integer_spec)

            two = dictobj.Field(sb.integer_spec, default=20
                , help = """
                    two
                    is
                    good
                  """
                )

            three = dictobj.Field(sb.string_spec, wrapper=sb.required, help="three")

        got = list(chp.fields_description(Thing))

        self.assertEqual(got
            , [ ("two", "integer (default 20)", "two\nis\ngood")
              , ("three", "string (required)", "three")
              ]
            )

    it "works for default fields":
        fields = {
              "finder_field": None
            , "target_field": None
            , "db_queue_field": None
            , "commander_field": None
            , "progress_cb_field": None
            , "final_future_field": None
            , "request_future_field": None
            , "server_options_field": None
            , "request_handler_field": None
            , "protocol_register_field": None

            , "refresh_field": "boolean"
            , "timeout_field": "float (default 20)"
            , "matcher_field": "string or dictionary"
            , "pkt_type_field": "integer or string (required)"
            , "pkt_args_field": "dictionary"
            }

        have = []

        for field in dir(df):
            if isinstance(getattr(df, field), dictobj.Field):
                have.append(field)

        if sorted(fields) != sorted(have):
            assert False, f"test is missing default fields, looking for {sorted(fields)}, but have defined {sorted(have)}"

        Thing = type("Thing", (dictobj.Spec, ), {field: getattr(df, field) for field in fields})

        got = []
        for name, type_info, hlp in chp.fields_description(Thing):
            self.assertEqual(dedent(getattr(df, name).help).strip(), hlp)
            assert fields.get(name) is not None, f"Expected this field to not be used {name}"
            self.assertEqual(fields[name], type_info
                , f"Expect field type info to be correct for {name}: got '{type_info}' instead of '{fields[name]}'"
                )
            got.append(name)

        self.assertEqual(sorted(got), sorted(name for name in fields if fields.get(name) is not None))

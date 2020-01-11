# coding: spec

from photons_interactor.commander import default_fields as df
from photons_interactor.commander import helpers as chp

from photons_app.test_helpers import TestCase

from delfick_project.norms import dictobj, sb
from textwrap import dedent

describe TestCase, "fields_description":
    it "only gets fields that have help specified":

        class Thing(dictobj.Spec):
            one = dictobj.Field(sb.integer_spec)

            two = dictobj.Field(
                sb.integer_spec,
                default=20,
                help="""
                    two
                    is
                    good
                  """,
            )

            three = dictobj.Field(sb.string_spec, wrapper=sb.required, help="three")

        got = list(chp.fields_description(Thing))

        assert got == [
            ("two", "integer (default 20)", "two\nis\ngood"),
            ("three", "string (required)", "three"),
        ]

    it "works for default fields":
        fields = {
            "refresh_field": "boolean",
            "timeout_field": "float (default 20)",
            "matcher_field": "string or dictionary",
            "pkt_type_field": "integer or string (required)",
            "pkt_args_field": "dictionary",
        }

        have = []

        for field in dir(df):
            if isinstance(getattr(df, field), dictobj.Field):
                have.append(field)

        if sorted(fields) != sorted(have):
            assert (
                False
            ), f"test is missing default fields, looking for {sorted(fields)}, but have defined {sorted(have)}"

        Thing = type("Thing", (dictobj.Spec,), {field: getattr(df, field) for field in fields})

        got = []
        for name, type_info, hlp in chp.fields_description(Thing):
            assert dedent(getattr(df, name).help).strip() == hlp
            assert fields.get(name) is not None, f"Expected this field to not be used {name}"
            assert (
                fields[name] == type_info
            ), f"Expect field type info to be correct for {name}: got '{type_info}' instead of '{fields[name]}'"
            got.append(name)

        assert sorted(got) == sorted(name for name in fields if fields.get(name) is not None)

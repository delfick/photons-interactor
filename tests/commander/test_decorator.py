# coding: spec

from photons_interactor.commander.decorator import command, command_spec

from photons_app.test_helpers import TestCase

from input_algorithms.errors import BadSpecValue
from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from input_algorithms.meta import Meta
from unittest import mock

describe TestCase, "command":
    it "sets kls and FieldSpec for that name in available_commands":
        class CommandBlah(dictobj.Spec):
            one = dictobj.Field(sb.integer_spec)
            two = dictobj.Field(sb.string_spec)

        class CommandMeh(dictobj.Spec):
            three = dictobj.Field(sb.overridden("{thing}"), formatted=True)
            four = dictobj.Field(sb.string_spec)

        available_commands = {}
        with mock.patch.object(command, "available_commands", available_commands):
            command(name="blah")(CommandBlah)
            command(name="meh")(CommandMeh)

        assert CommandBlah.__interactor_command__
        assert CommandMeh.__interactor_command__

        self.assertEqual(available_commands
            , { "blah": {"kls": CommandBlah, "spec": mock.ANY}
              , "meh": {"kls": CommandMeh, "spec": mock.ANY}
              }
            )

        blah = available_commands["blah"]["spec"].empty_normalise(one=1, two="three")
        meh = available_commands["meh"]["spec"].normalise(
              Meta({"thing": "stuff"}, []).at("<input>")
            , dict(four="fourvalue")
            )

        assert isinstance(blah, CommandBlah)
        assert isinstance(meh, CommandMeh)

        self.assertEqual(blah.one, 1)
        self.assertEqual(blah.two, "three")

        self.assertEqual(meh.three, "stuff")
        self.assertEqual(meh.four, "fourvalue")

describe TestCase, "command_spec":
    it "can turn dictionary into a command":
        class CommandMeh(dictobj.Spec):
            three = dictobj.Field(sb.overridden("{thing}"), formatted=True)
            four = dictobj.Field(sb.string_spec)

        meta = Meta({"thing": "tree"}, []).at("<input>")

        available_commands = {}
        with mock.patch.object(command, "available_commands", available_commands):
            command(name="meh")(CommandMeh)
            instance = command_spec().normalise(meta, {"command": "meh", "args": {"four": "stuff"}})

        assert isinstance(instance, CommandMeh)
        self.assertEqual(instance.three, "tree")
        self.assertEqual(instance.four, "stuff")

    it "complains if we don't have command":
        meta = Meta.empty()
        error = BadSpecValue("Expected a value but got none", meta=meta.at("command"))

        with self.fuzzyAssertRaisesError(BadSpecValue, _errors=[error]):
            command_spec().normalise(Meta.empty(), {})

    it "complains if command isn't registered":
        meta = Meta.empty().at("<input>")

        available_commands = {}
        with self.fuzzyAssertRaisesError(BadSpecValue, "Unknown command", wanted="meh", available=[]):
            with mock.patch.object(command, "available_commands", available_commands):
                command_spec().normalise(meta, {"command": "meh", "args": {"four": "stuff"}})

# coding: spec

from photons_interactor.database.models import scene_spec

from photons_app.test_helpers import TestCase, print_packet_difference

from photons_messages import LightMessages, MultiZoneMessages, TileMessages

from noseOfYeti.tokeniser.support import noy_sup_setUp
from input_algorithms.errors import BadSpecValue
from input_algorithms import spec_base as sb
from input_algorithms.dictobj import dictobj
from input_algorithms.meta import Meta
from unittest import mock
import random
import json
import uuid

meta = Meta.empty()

describe TestCase, "range_spec":
    it "complains if the value isn't a float":
        for val in (True, False, {}, [], None, lambda: 1):
            with self.fuzzyAssertRaisesError(BadSpecValue):
                scene_spec.range_spec(0, 1).normalise(meta, val)

    it "can use the spec that is provided":
        got = scene_spec.range_spec(0, 1, sb.integer_spec()).normalise(meta, 0)
        self.assertEqual(got, 0)
        self.assertEqual(type(got), int)

        # Prove it's not an integer without specifying integer_spec
        got = scene_spec.range_spec(0, 1).normalise(meta, 0)
        self.assertEqual(got, 0.0)
        self.assertEqual(type(got), float)

    it "complains if less than minimum":
        for val in (-1.0, -2.0, -3.0):
            with self.fuzzyAssertRaisesError(BadSpecValue, "Number must be between min and max", minimum=0, maximum=1, got=val, meta=meta):
                scene_spec.range_spec(0, 1).normalise(meta, val)

    it "complains if greater than maximum":
        for val in (1.1, 2.0, 3.0):
            with self.fuzzyAssertRaisesError(BadSpecValue, "Number must be between min and max", minimum=0, maximum=1, got=val, meta=meta):
                scene_spec.range_spec(0, 1).normalise(meta, val)


    it "works if number is between min and max":
        for val in (0.1, 0.5, 0.9):
            self.assertEqual(scene_spec.range_spec(0, 1).normalise(meta, val), val)

describe TestCase, "sized_list_spec":
    it "complains if not matching the spec":
        val = [1, 2, None]
        spec = scene_spec.sized_list_spec(sb.integer_spec(), 4)
        with self.fuzzyAssertRaisesError(BadSpecValue):
            spec.normalise(meta, val)

    it "complains if list is not the correct length":
        spec = scene_spec.sized_list_spec(sb.integer_spec(), 2)
        with self.fuzzyAssertRaisesError(BadSpecValue, "Expected certain number of parts", want=2, got=1):
            spec.normalise(meta, 1)

        with self.fuzzyAssertRaisesError(BadSpecValue, "Expected certain number of parts", want=2, got=1):
            spec.normalise(meta, [1])

        with self.fuzzyAssertRaisesError(BadSpecValue, "Expected certain number of parts", want=2, got=3):
            spec.normalise(meta, [1, 2, 3])

    it "returns the list if correct length":
        spec = scene_spec.sized_list_spec(sb.string_spec(), 1)

        got = spec.normalise(meta, "one")
        self.assertEqual(got, ["one"])

        got = spec.normalise(meta, ["one"])
        self.assertEqual(got, ["one"])

        spec = scene_spec.sized_list_spec(sb.string_spec(), 2)
        got = spec.normalise(meta, ["one", "two"])
        self.assertEqual(got, ["one", "two"])

describe TestCase, "hsbk":
    it "expects 4 items":
        spec = scene_spec.hsbk()

        val = [200, 1, 1, 3500]
        self.assertEqual(spec.normalise(meta, val), val)

    it "complains if hue is outside 0 and 360":
        spec = scene_spec.hsbk()

        with self.fuzzyAssertRaisesError(BadSpecValue, "Number must be between min and max", minimum=0, maximum=360):
            spec.normalise(meta, [-1, 1, 1, 3500])

        with self.fuzzyAssertRaisesError(BadSpecValue, "Number must be between min and max", minimum=0, maximum=360):
            spec.normalise(meta, [361, 1, 1, 3500])

    it "complains if saturation is outside 0 and 1":
        spec = scene_spec.hsbk()

        with self.fuzzyAssertRaisesError(BadSpecValue, "Number must be between min and max", minimum=0, maximum=1):
            spec.normalise(meta, [1, -0.1, 1, 3500])

        with self.fuzzyAssertRaisesError(BadSpecValue, "Number must be between min and max", minimum=0, maximum=1):
            spec.normalise(meta, [360, 1.1, 1, 3500])

    it "complains if brightness is outside 0 and 1":
        spec = scene_spec.hsbk()

        with self.fuzzyAssertRaisesError(BadSpecValue, "Number must be between min and max", minimum=0, maximum=1):
            spec.normalise(meta, [1, 0, -0.1, 3500])

        with self.fuzzyAssertRaisesError(BadSpecValue, "Number must be between min and max", minimum=0, maximum=1):
            spec.normalise(meta, [360, 1, 1.1, 3500])

    it "complains if kelvin is outside 2500 and 9000":
        spec = scene_spec.hsbk()

        with self.fuzzyAssertRaisesError(BadSpecValue, "Number must be between min and max", minimum=2500, maximum=9000):
            spec.normalise(meta, [1, 0, 0, 2499])

        with self.fuzzyAssertRaisesError(BadSpecValue, "Number must be between min and max", minimum=2500, maximum=9000):
            spec.normalise(meta, [360, 1, 1, 9001])

describe TestCase, "chain_spec":
    it "complains if list is not 64":
        chain = []
        for i in range(63):
            chain.append([0, 0, 0, 2500])

        spec = scene_spec.chain_spec
        with self.fuzzyAssertRaisesError(BadSpecValue, "Expected certain number of parts", want=64, got=63):
            spec.normalise(meta, chain)

        chain.extend([[0, 0, 0, 2500], [1, 1, 1, 9000]])
        with self.fuzzyAssertRaisesError(BadSpecValue, "Expected certain number of parts", want=64, got=65):
            spec.normalise(meta, chain)

describe TestCase, "json_string_spec":
    describe "storing":
        it "loads if the val is a string and returns as dumps":
            spec = sb.set_options(one=sb.integer_spec())
            spec = scene_spec.json_string_spec(spec, True)
            got = spec.normalise(meta, '{"one": 2, "two": 3}')
            self.assertEqual(got, '{"one": 2}')

        it "doesn't loads if not a string and returns as dumps":
            spec = sb.set_options(one=sb.integer_spec())
            spec = scene_spec.json_string_spec(spec, True)
            got = spec.normalise(meta, {"one": 2, "two": 3})
            self.assertEqual(got, '{"one": 2}')

        it "complains if string is not valid json":
            spec = sb.set_options(one=sb.integer_spec())
            spec = scene_spec.json_string_spec(spec, True)
            with self.fuzzyAssertRaisesError(BadSpecValue, "Value was not valid json"):
                spec.normalise(meta, '{')

        it "complains if we don't match our spec":
            spec = sb.set_options(one=sb.required(sb.integer_spec()))
            spec = scene_spec.json_string_spec(spec, True)
            with self.fuzzyAssertRaisesError(BadSpecValue):
                spec.normalise(meta, '{"two": 3}')

    describe "not storing":
        it "loads if the val is a string":
            spec = sb.set_options(one=sb.integer_spec())
            spec = scene_spec.json_string_spec(spec, False)
            got = spec.normalise(meta, '{"one": 2, "two": 3}')
            self.assertEqual(got, {"one": 2})

        it "doesn't loads if not a string":
            spec = sb.set_options(one=sb.integer_spec())
            spec = scene_spec.json_string_spec(spec, False)
            got = spec.normalise(meta, {"one": 2, "two": 3})
            self.assertEqual(got, {"one": 2})

        it "complains if we don't match our spec":
            spec = sb.set_options(one=sb.required(sb.integer_spec()))
            spec = scene_spec.json_string_spec(spec, False)
            with self.fuzzyAssertRaisesError(BadSpecValue):
                spec.normalise(meta, {"two": 3})

describe TestCase, "make_spec":
    describe "storing":
        it "has nullable fields for everything but uuid and matcher":
            spec = scene_spec.make_spec(storing=True)
            obj = spec.normalise(meta, {"uuid": "one", "matcher": {"label": "kitchen"}})
            self.assertEqual(obj.as_dict()
                , { "uuid": "one"
                  , "matcher": '{"label": "kitchen"}'
                  , "power": None
                  , "color": None
                  , "zones": None
                  , "chain": None
                  , "duration": None
                  }
                )

            with self.fuzzyAssertRaisesError(BadSpecValue):
                obj = spec.normalise(meta, {"uuid": "one"})

            with self.fuzzyAssertRaisesError(BadSpecValue):
                obj = spec.normalise(meta, {"matcher": {"label": "kitchen"}})

        it "makes a class with no extra methods and makes json into text":
            zones = []
            for i in range(10):
                zones.append([float(i), 1.0, 0.0, 3500])

            chain = []
            for i in range(5):
                tile = []
                for j in range(64):
                    tile.append([float(j), 0.0, 1.0, 2500])
                chain.append(tile)

            spec = scene_spec.make_spec(storing=True)
            identifier = str(uuid.uuid1())

            obj = spec.normalise(meta
                , { "uuid": identifier
                  , "matcher": {"label": "den"}
                  , "power": True
                  , "color": "red"
                  , "zones": zones
                  , "chain": chain
                  , "duration": 1
                  }
                )

            class base(dictobj.Spec):
                pass

            got = dir(obj)
            diff = set(got) - set(dir(base()))
            self.assertEqual(diff, set(["uuid", "matcher", "power", "color", "zones", "chain", "duration"]))

            self.assertEqual(obj.as_dict()
                , { "uuid": identifier
                  , "matcher": '{"label": "den"}'
                  , "power": True
                  , "color": "red"
                  , "zones": json.dumps(zones)
                  , "chain": json.dumps(chain)
                  , "duration": 1
                  }
                )

    describe "not storing":
        before_each:
            self.zones = []
            for i in range(10):
                self.zones.append([float(i), 1.0, 0.0, 3500])

            self.chain = []
            for i in range(5):
                tile = []
                for j in range(64):
                    tile.append([float(j), 0.0, 1.0, 2500])
                self.chain.append(tile)

            self.spec = scene_spec.make_spec(storing=False)
            self.identifier = str(uuid.uuid1())

            self.kwargs = {
                    "uuid": self.identifier
                  , "matcher": {"label": "den"}
                  , "power": True
                  , "color": "red"
                  , "zones": self.zones
                  , "chain": self.chain
                  , "duration": 1
                  }

            self.obj = self.spec.normalise(meta, self.kwargs)

        it "has nullable fields for everything but uuid and matcher":
            spec = scene_spec.make_spec(storing=False)
            obj = spec.normalise(meta, {"uuid": "one", "matcher": {"label": "kitchen"}})
            self.assertEqual(obj.as_dict()
                , { "uuid": "one"
                  , "matcher": {"label": "kitchen"}
                  , "power": None
                  , "color": None
                  , "zones": None
                  , "chain": None
                  , "duration": None
                  }
                )

            with self.fuzzyAssertRaisesError(BadSpecValue):
                obj = spec.normalise(meta, {"uuid": "one"})

            with self.fuzzyAssertRaisesError(BadSpecValue):
                obj = spec.normalise(meta, {"matcher": {"label": "kitchen"}})

        it "does not store as text":
            for key, val in self.kwargs.items():
                self.assertEqual(getattr(self.obj, key), val)

        describe "transform_options":
            it "takes into account power, color and duration":
                self.assertEqual(self.obj.transform_options
                    , { "power": "on"
                      , "color": "red"
                      , "duration": 1
                      }
                    )

                self.obj.power = False
                self.assertEqual(self.obj.transform_options
                    , { "power": "off"
                      , "color": "red"
                      , "duration": 1
                      }
                    )

                self.obj.color = None
                self.assertEqual(self.obj.transform_options
                    , { "power": "off"
                      , "duration": 1
                      }
                    )

                self.obj.duration = None
                self.assertEqual(self.obj.transform_options
                    , { "power": "off"
                      }
                    )

                self.obj.power = None
                self.assertEqual(self.obj.transform_options, {})

        describe "colors_from_hsbks":
            it "takes uses hsbks if no overrides":
                hsbks = []
                result = []
                for i in range(10):
                    hue = random.randrange(0, 360)
                    saturation = random.randrange(0, 10) / 10
                    brightness = random.randrange(0, 10) / 10
                    kelvin = random.randrange(2500, 9000)

                    hsbks.append([hue, saturation, brightness, kelvin])
                    result.append(
                          { "hue": hue
                          , "saturation": saturation
                          , "brightness": brightness
                          , "kelvin": kelvin
                          }
                        )

                    self.assertEqual(self.obj.colors_from_hsbks(hsbks, {}), result)

            it "takes overrides from overrides":
                h = mock.Mock(name="hue")
                s = mock.Mock(name="saturation")
                b = mock.Mock(name="brightness")
                k = mock.Mock(name="kelvin")

                o1 = {"hue": h}
                o2 = {"saturation": s}
                o3 = {"brightness": b}
                o4 = {"kelvin": k}
                o5 = {"hue": h, "saturation": s}
                o6 = {"brightness": b, "kelvin": k}

                for overrides in (o1, o2, o3, o4, o5, o6):
                    hsbks = []
                    result = []
                    for i in range(10):
                        hue = random.randrange(0, 360)
                        saturation = random.randrange(0, 10) / 10
                        brightness = random.randrange(0, 10) / 10
                        kelvin = random.randrange(2500, 9000)

                        hsbks.append([hue, saturation, brightness, kelvin])
                        want = {
                             "hue": hue
                           , "saturation": saturation
                           , "brightness": brightness
                           , "kelvin": kelvin
                           }
                        want.update(overrides)
                        result.append(want)

                    self.assertEqual(
                          self.obj.colors_from_hsbks(hsbks, overrides)
                        , result
                        )

        describe "power_message":
            it "does not provide SetLightPower if we have no power":
                self.obj.power = None
                msg = self.obj.power_message({})
                self.assertIs(msg, None)

            it "provides power if in overrides":
                self.obj.power = None
                self.obj.duration = None

                msg = self.obj.power_message({"power": "on"})
                self.assertEqual(msg
                    , LightMessages.SetLightPower(level = 65535, duration=0)
                    )

                msg = self.obj.power_message({"power": True})
                self.assertEqual(msg
                    , LightMessages.SetLightPower(level = 65535, duration=0)
                    )

                msg = self.obj.power_message({"power": False})
                self.assertEqual(msg
                    , LightMessages.SetLightPower(level = 0, duration=0)
                    )

                msg = self.obj.power_message({"power": "off"})
                self.assertEqual(msg
                    , LightMessages.SetLightPower(level = 0, duration=0)
                    )

                self.obj.duration = 2
                msg = self.obj.power_message({"power": "off"})
                self.assertEqual(msg
                    , LightMessages.SetLightPower(level = 0, duration=2)
                    )

            it "provides power if on the object":
                self.obj.power = True
                self.obj.duration = 3

                msg = self.obj.power_message({})
                self.assertEqual(msg
                    , LightMessages.SetLightPower(level = 65535, duration=3)
                    )

                self.obj.power = False
                msg = self.obj.power_message({})
                self.assertEqual(msg
                    , LightMessages.SetLightPower(level = 0, duration=3)
                    )

        describe "zone_msgs":
            before_each:
                self.overrides = mock.Mock(name="overrides")

            it "yields power message if we have one":
                msg = mock.Mock(name="msg")
                power_message = mock.Mock(name="power_message", return_value=msg)

                with mock.patch.object(self.obj, "power_message", power_message):
                    itr = iter(self.obj.zone_msgs(self.overrides))
                    m = next(itr)
                    self.assertIs(m, msg)

                power_message.assert_called_once_with(self.overrides)

            it "does not yield power message if we don't have one":
                power_message = mock.Mock(name="power_message", return_value=None)
                colors = self.obj.colors_from_hsbks(self.obj.zones, {})
                colors_from_hsbks = mock.Mock(name="colors_from_hsbks", return_value=colors)
                determine_duration = mock.Mock(name="determine_duration", return_value=1)

                with mock.patch.multiple(self.obj
                    , power_message = power_message
                    , colors_from_hsbks = colors_from_hsbks
                    , determine_duration = determine_duration
                    ):
                    itr = iter(self.obj.zone_msgs(self.overrides))
                    m = next(itr)
                    self.assertIs(type(m), MultiZoneMessages.SetColorZones)

                power_message.assert_called_once_with(self.overrides)
                colors_from_hsbks.assert_called_once_with(self.obj.zones, self.overrides)
                determine_duration.assert_called_once_with(self.overrides)

            describe "Yielding SetMultiZoneColorZones messages":
                def setter(self, h, s, b, k, **kwargs):
                    return MultiZoneMessages.SetColorZones(
                      hue = h, saturation = s, brightness = b, kelvin = k
                    , res_required=False
                    , **kwargs
                    )

                def assertCorrect(self, zones, *want):
                    power_message = mock.Mock(name="power_message", return_value=None)

                    colors = self.obj.colors_from_hsbks(zones, {})
                    colors_from_hsbks = mock.Mock(name="colors_from_hsbks", return_value=colors)

                    determine_duration = mock.Mock(name="determine_duration", return_value=1)

                    with mock.patch.multiple(self.obj
                        , power_message = power_message
                        , colors_from_hsbks = colors_from_hsbks
                        , determine_duration = determine_duration
                        ):
                        msgs = list(self.obj.zone_msgs(self.overrides))

                    if msgs != want:
                        for i, (w, m) in enumerate(zip(want, msgs)):
                            if w != m:
                                print(f"Message {i}:")
                                print_packet_difference(w, m)

                    self.assertEqual(len(want), len(msgs))
                    self.assertEqual(list(want), msgs)

                    power_message.assert_called_once_with(self.overrides)
                    colors_from_hsbks.assert_called_once_with(self.obj.zones, self.overrides)
                    determine_duration.assert_called_once_with(self.overrides)

            it "works":
                zones = [
                      [0, 0, 0, 3500]
                    , [0, 0, 0, 3500]
                    , [0, 0, 0, 3500]
                    , [100, 1, 0, 3500]
                    , [100, 0.5, 0, 3500]
                    , [100, 0.5, 0, 3500]
                    , [100, 0.5, 1, 3500]
                    , [100, 0.5, 1, 9000]
                    , [100, 0.5, 1, 9000]
                    ]

                self.assertCorrect(zones
                    , self.setter(0, 0, 0, 3500, start_index=0, end_index=2, duration=1)
                    , self.setter(100, 1, 0, 3500, start_index=3, end_index=3, duration=1)
                    , self.setter(100, 0.5, 0, 3500, start_index=4, end_index=5, duration=1)
                    , self.setter(100, 0.5, 1, 3500, start_index=6, end_index=6, duration=1)
                    , self.setter(100, 0.5, 1, 9000, start_index=7, end_index=8, duration=1)
                    )

            it "works2":
                zones = [
                      [0, 0, 0, 3500]
                    , [100, 1, 0, 3500]
                    , [100, 0.5, 0, 3500]
                    , [100, 0.5, 0, 3500]
                    , [100, 0.5, 1, 3500]
                    , [100, 0.5, 1, 9000]
                    ]

                self.assertCorrect(zones
                    , self.setter(0, 0, 0, 3500, start_index=0, end_index=0, duration=1)
                    , self.setter(100, 1, 0, 3500, start_index=1, end_index=1, duration=1)
                    , self.setter(100, 0.5, 0, 3500, start_index=2, end_index=3, duration=1)
                    , self.setter(100, 0.5, 1, 3500, start_index=4, end_index=4, duration=1)
                    , self.setter(100, 0.5, 1, 9000, start_index=5, end_index=5, duration=1)
                    )

        describe "chain_msgs":
            before_each:
                self.overrides = mock.Mock(name="overrides")

            it "yields power message if we have one":
                msg = mock.Mock(name="msg")
                power_message = mock.Mock(name="power_message", return_value=msg)

                with mock.patch.object(self.obj, "power_message", power_message):
                    itr = iter(self.obj.chain_msgs(self.overrides))
                    m = next(itr)
                    self.assertIs(m, msg)

                power_message.assert_called_once_with(self.overrides)

            it "does not yield power message if we don't have one":
                power_message = mock.Mock(name="power_message", return_value=None)
                colors = self.obj.colors_from_hsbks(self.obj.zones, {})
                colors_from_hsbks = mock.Mock(name="colors_from_hsbks", return_value=colors)
                determine_duration = mock.Mock(name="determine_duration", return_value=1)

                with mock.patch.multiple(self.obj
                    , power_message = power_message
                    , colors_from_hsbks = colors_from_hsbks
                    , determine_duration = determine_duration
                    ):
                    itr = iter(self.obj.chain_msgs(self.overrides))
                    m = next(itr)
                    self.assertIs(type(m), TileMessages.Set64)

                power_message.assert_called_once_with(self.overrides)
                colors_from_hsbks.assert_called_once_with(self.obj.chain[0], self.overrides)
                determine_duration.assert_called_once_with(self.overrides)

            describe "yielding Set64 messages":
                def setter(self, **kwargs):
                    return TileMessages.Set64(
                          length=1
                        , x=0
                        , y=0
                        , width=8
                        , res_required=False
                        , **kwargs
                        )

                it "works":
                    power_message = mock.Mock(name="power_message", return_value=None)

                    original = self.obj.colors_from_hsbks
                    returned = [original(c, {}) for c in self.obj.chain]

                    def colors_from_hsbks(c, o):
                        self.assertIs(o, self.overrides)
                        return original(c, {})
                    colors_from_hsbks = mock.Mock(name="colors_from_hsbks", side_effect=colors_from_hsbks)

                    determine_duration = mock.Mock(name="determine_duration", return_value=1)

                    with mock.patch.multiple(self.obj
                        , power_message = power_message
                        , colors_from_hsbks = colors_from_hsbks
                        , determine_duration = determine_duration
                        ):
                        msgs = list(self.obj.chain_msgs(self.overrides))

                    want = [
                          self.setter(tile_index=0, duration=1, colors=returned[0])
                        , self.setter(tile_index=1, duration=1, colors=returned[1])
                        , self.setter(tile_index=2, duration=1, colors=returned[2])
                        , self.setter(tile_index=3, duration=1, colors=returned[3])
                        , self.setter(tile_index=4, duration=1, colors=returned[4])
                        ]

                    if msgs != want:
                        for i, (w, m) in enumerate(zip(want, msgs)):
                            if w != m:
                                print(f"Message {i}:")
                                print_packet_difference(w, m)

                    self.assertEqual(len(want), len(msgs))
                    self.assertEqual(list(want), msgs)

                    power_message.assert_called_once_with(self.overrides)
                    determine_duration.assert_called_once_with(self.overrides)

                    self.assertEqual(colors_from_hsbks.mock_calls
                        , [ mock.call(self.obj.chain[0], self.overrides)
                          , mock.call(self.obj.chain[1], self.overrides)
                          , mock.call(self.obj.chain[2], self.overrides)
                          , mock.call(self.obj.chain[3], self.overrides)
                          , mock.call(self.obj.chain[4], self.overrides)
                          ]
                        )

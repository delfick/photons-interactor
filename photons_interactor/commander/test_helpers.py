from photons_app.formatter import MergedOptionStringFormatter
from photons_app.test_helpers import print_packet_difference
from photons_app.registers import ProtocolRegister

from photons_socket.fake import FakeDevice, MemorySocketTarget, MemorySocketBridge
from photons_products_registry import LIFIProductRegistry, capability_for_ids
from photons_socket.messages import DiscoveryMessages
from photons_device_messages import DeviceMessages
from photons_multizone import MultiZoneMessages
from photons_protocol.frame import LIFXPacket
from photons_colour import ColourMessages

from input_algorithms.dictobj import dictobj
from input_algorithms.meta import Meta

from contextlib import contextmanager
from unittest import mock
import uuid

def make_protocol_register():
    protocol_register = ProtocolRegister()
    protocol_register.add(1024, LIFXPacket)
    protocol_register.message_register(1024).add(MultiZoneMessages)
    protocol_register.message_register(1024).add(DiscoveryMessages)
    protocol_register.message_register(1024).add(DeviceMessages)
    protocol_register.message_register(1024).add(ColourMessages)
    return protocol_register

def make_memory_target(final_future):
    everything = {
          "final_future": final_future
        , "protocol_register": make_protocol_register()
        }
    meta = Meta(everything, []).at("target")
    return MemorySocketTarget.FieldSpec(formatter=MergedOptionStringFormatter).normalise(meta, {})

class MemoryTargetRunner:
    def __init__(self, target, devices):
        self.target = target
        self.devices = devices

    async def __aenter__(self):
        await self.start()

    async def start(self):
        for device in self.devices:
            await device.start()
            self.target.add_device(device)

    async def __aexit__(self, typ, exc, tb):
        await self.close()

    async def close(self):
        for device in self.target.devices.values():
            await device.finish()

class Group(dictobj):
    fields = ["name", "uuid", "updated_at"]

class Color(dictobj):
    fields = ["hue", "saturation", "brightness", "kelvin"]

class Firmware(dictobj):
    fields = ["version", "build_time"]

def fake_devices(protocol_register):
    identifier = lambda : str(uuid.uuid4()).replace('-', "")

    group_one = Group("Living Room", identifier(), 0)
    group_two = Group("Bathroom", identifier(), 0)
    location_one = Group("Home", identifier(), 0)

    location_two = Group("Work", identifier(), 0)
    group_three = Group("desk", identifier(), 0)

    a19_1 = Device("d073d5000001", protocol_register
        , label = "kitchen"
        , power = 0
        , group = group_one
        , location = location_one
        , color = Color(0, 1, 1, 2500)
        , vendor_id = 1
        , product_id = LIFIProductRegistry.LCM2_A19.value
        , firmware = Firmware("2.75", 1521690429)
        )

    a19_2 = Device("d073d5000002", protocol_register
        , label = "bathroom"
        , power = 65535
        , group = group_two
        , location = location_one
        , color = Color(100, 1, 1, 2500)
        , vendor_id = 1
        , product_id = LIFIProductRegistry.LCM2_A19.value
        , firmware = Firmware("2.75", 1521690429)
        )

    color1000 = Device("d073d5000003", protocol_register
        , label = "lamp"
        , power = 65535
        , group = group_three
        , location = location_two
        , color = Color(100, 0, 1, 2500)
        , vendor_id = 1
        , product_id = LIFIProductRegistry.LCMV4_A19_COLOR.value
        , firmware = Firmware("1.1", 1530327089)
        )

    white800 = Device("d073d5000004", protocol_register
        , label = "lamp"
        , power = 65535
        , group = group_three
        , location = location_two
        , color = Color(100, 0, 1, 2500)
        , vendor_id = 1
        , product_id = LIFIProductRegistry.LCMV4_A19_WHITE_LV.value
        , firmware = Firmware("1.1", 1530327089)
        )

    strip1 = Device("d073d5000005", protocol_register
        , label = "desk"
        , power = 65535
        , group = group_one
        , location = location_one
        , color = Color(200, 0.5, 0.5, 2500)
        , vendor_id = 1
        , product_id = LIFIProductRegistry.LCM2_Z.value
        , firmware = Firmware("2.75", 1521690429)
        )

    strip2 = Device("d073d5000006", protocol_register
        , label = "tv"
        , power = 65535
        , group = group_three
        , location = location_two
        , color = Color(200, 0.5, 0.5, 2500)
        , vendor_id = 1
        , product_id = LIFIProductRegistry.LCM1_Z.value
        , firmware = Firmware("1.1", 1530327089)
        )

    return {
          "groups":
          { group_one.name: group_one
          , group_two.name: group_two
          , group_three.name: group_three
          }
        , "locations": {location_one.name: location_one, location_two.name: location_two}
        , "devices": [a19_1, a19_2, color1000, white800, strip1, strip2]
        }

class Device(FakeDevice):
    def __init__(self, serial, protocol_register, *, label, power, group, location, color, vendor_id, product_id, firmware):
        super().__init__(serial, protocol_register)

        def reset():
            self.gets = []
            self.sets = []

            self.change_hsbk(color)
            self.change_label(label)
            self.change_power(power)
            self.change_infrared(0)

            for k, v in [("group", group), ("location", location)]:
                setattr(self, k, "")
                setattr(self, f"{k}_label", "")
                setattr(self, f"{k}_updated_at", 0)
                if v:
                    getattr(self, f"change_{k}")(v)

            self.change_firmware(firmware)
            self.change_version(vendor_id, product_id)

        self.reset = reset
        reset()

    def change_infrared(self, level):
        self.infrared = level

    def change_label(self, label):
        self.label = label

    def change_power(self, power):
        self.power = power

    def change_hsbk(self, color):
        self.hue = color.hue
        self.saturation = color.saturation
        self.brightness = color.brightness
        self.kelvin = color.kelvin

    def change_group(self, group):
        self.group = group.uuid
        self.group_label = group.name
        self.group_updated_at = group.updated_at

    def change_location(self, location):
        self.location = location.uuid
        self.location_label = location.name
        self.location_updated_at = location.updated_at

    def change_firmware(self, firmware):
        self.firmware_version = firmware.version
        self.firmware_build_time = firmware.build_time

    def change_version(self, vendor_id, product_id):
        self.vendor_id = vendor_id
        self.product_id = product_id

    @contextmanager
    def offline(self):
        try:
            self.online = False
            yield
        finally:
            self.online = True

    @property
    def capability(self):
        return capability_for_ids(self.product_id, self.vendor_id)

    def light_state_message(self):
        return ColourMessages.LightState(
              hue = self.hue
            , saturation = self.saturation
            , brightness = self.brightness
            , power = self.power
            , label = self.label
            )

    def clearGetMessages(self):
        self.gets = []

    def clearSetMessages(self):
        self.sets = []

    def expectNoSetMessages(self):
        assert len(self.sets) == 0, f"Expected no set messages, have {self.sets}"

    def expectNoGetMessages(self):
        assert len(self.gets) == 0, f"Expected no get messages, have {self.gets}"

    def expectSetMessages(self, *msgs):
        return self.expectMessages("sets", *msgs)

    def expectGetMessages(self, *msgs):
        return self.expectMessages("gets", *msgs)

    def expectMessages(self, typ, *msgs):
        lst = getattr(self, typ)

        assert len(lst) == len(msgs), f"{self.serial}: Expected same messages, got {[type(s) for s in self.sets]}, want {[type(m) for m in msgs]}"
        for i, (got, want) in enumerate(zip(lst, msgs)):
            if type(got) != type(want):
                assert type(got) == type(want), f"{self.serial}: msg#{i}: Message of different type, got {type(got)} wanted {type(want)}"

            if repr(got.payload) != repr(want.payload):
                print_packet_difference(got, want)
            assert repr(got.payload) == repr(want.payload), f"{self.serial}: msg#{i}: Expected payloads to be the same, got {repr(got.payload)}, want {repr(want.payload)}"

            assert got.res_required == want.res_required, f"{self.serial}: msg#{i}: Expected same res_required, got {got}, want {want}"
            assert got.ack_required == want.ack_required, f"{self.serial}: msg#{i}: Expected same ack_required, got {got}, want {want}"

        setattr(self, typ, [])

    def make_response(self, pkt):
        if pkt.__class__.__name__.startswith("Get"):
            self.gets.append(pkt)
        else:
            self.sets.append(pkt)

        if pkt | DeviceMessages.GetInfrared:
            return DeviceMessages.StateInfrared(level=self.infrared)

        if pkt | ColourMessages.GetColor:
            return self.light_state_message()

        elif pkt | DeviceMessages.GetVersion:
            return DeviceMessages.StateVersion(
                  vendor = self.vendor_id
                , product = self.product_id
                , version = 0
                )

        elif pkt | DeviceMessages.GetHostFirmware:
            return DeviceMessages.StateHostFirmware(
                  version = self.firmware_version
                , build = self.firmware_build_time
                )

        elif pkt | DeviceMessages.GetGroup:
            return DeviceMessages.StateGroup(
                  group = self.group
                , label = self.group_label
                , updated_at = self.group_updated_at
                )

        elif pkt | DeviceMessages.GetLocation:
            return DeviceMessages.StateLocation(
                  location = self.location
                , label = self.location_label
                , updated_at = self.location_updated_at
                )

        elif pkt | ColourMessages.SetWaveFormOptional or pkt | ColourMessages.SetColor:
            self.change_hsbk(Color(pkt.hue, pkt.saturation, pkt.brightness, pkt.kelvin))
            return self.light_state_message()

        elif pkt | DeviceMessages.SetLabel:
            self.change_label(pkt.label)
            return DeviceMessages.StateLabel(label=pkt.label)

        elif pkt | DeviceMessages.GetLabel:
            return DeviceMessages.StateLabel(label=self.label)

        elif pkt | DeviceMessages.SetPower or pkt | DeviceMessages.SetLightPower:
            res = DeviceMessages.StatePower(level=pkt.level)
            self.change_power(pkt.level)
            return res

        elif pkt | MultiZoneMessages.GetMultiZoneColorZones and self.capability.has_multizone:
            colors = []
            for i in range(16):
                colors.append(Color(i * 10, 1, 1, 2500).as_dict())

            return [
                  MultiZoneMessages.StateMultiZoneStateMultiZones(num_zones=16, zone_index=0, colors=colors[:8])
                , MultiZoneMessages.StateMultiZoneStateMultiZones(num_zones=16, zone_index=8, colors=colors[8:])
                ]

class Around:
    def __init__(self, val, gap=0.05):
        self.val = val
        self.gap = gap

    def __eq__(self, other):
        return other - self.gap < self.val < other + self.gap

    def __repr__(self):
        return f"<Around {self.val}>"

discovery_response = {
    "d073d5000001": {
        "brightness": 1.0,
        "cap": [
            "color",
            "not_chain",
            "not_ir",
            "not_multizone",
            "variable_color_temp"
        ],
        "firmware_version": "2.75",
        "group_id": mock.ANY,
        "group_name": "Living Room",
        "hue": 0.0,
        "kelvin": 3500,
        "label": "kitchen",
        "location_id": mock.ANY,
        "location_name": "Home",
        "power": "off",
        "product_id": 27,
        "product_identifier": "lifx_a19",
        "saturation": 1.0,
        "serial": "d073d5000001"
    },
    "d073d5000002": {
        "brightness": 1.0,
        "cap": [
            "color",
            "not_chain",
            "not_ir",
            "not_multizone",
            "variable_color_temp"
        ],
        "firmware_version": "2.75",
        "group_id": mock.ANY,
        "group_name": "Bathroom",
        "hue": Around(100),
        "kelvin": 3500,
        "label": "bathroom",
        "location_id": mock.ANY,
        "location_name": "Home",
        "power": "on",
        "product_id": 27,
        "product_identifier": "lifx_a19",
        "saturation": 1.0,
        "serial": "d073d5000002"
    },
    "d073d5000003": {
        "brightness": 1.0,
        "cap": [
            "color",
            "not_chain",
            "not_ir",
            "not_multizone",
            "variable_color_temp"
        ],
        "firmware_version": "1.1",
        "group_id": mock.ANY,
        "group_name": "desk",
        "hue": Around(100),
        "kelvin": 3500,
        "label": "lamp",
        "location_id": mock.ANY,
        "location_name": "Work",
        "power": "on",
        "product_id": 22,
        "product_identifier": "lifx_a19_color",
        "saturation": 0.0,
        "serial": "d073d5000003"
    },
    "d073d5000004": {
        "brightness": 1.0,
        "cap": [
            "not_chain",
            "not_color",
            "not_ir",
            "not_multizone",
            "variable_color_temp"
        ],
        "firmware_version": "1.1",
        "group_id": mock.ANY,
        "group_name": "desk",
        "hue": Around(100),
        "kelvin": 3500,
        "label": "lamp",
        "location_id": mock.ANY,
        "location_name": "Work",
        "power": "on",
        "product_id": 10,
        "product_identifier": "lifx_a19_white",
        "saturation": 0.0,
        "serial": "d073d5000004"
    },
    "d073d5000005": {
        "brightness": Around(0.5),
        "cap": [
            "color",
            "multizone",
            "not_chain",
            "not_ir",
            "variable_color_temp"
        ],
        "firmware_version": "2.75",
        "group_id": mock.ANY,
        "group_name": "Living Room",
        "hue": Around(200),
        "kelvin": 3500,
        "label": "desk",
        "location_id": mock.ANY,
        "location_name": "Home",
        "power": "on",
        "product_id": 32,
        "product_identifier": "lifx_z",
        "saturation": Around(0.5),
        "serial": "d073d5000005"
    },
    "d073d5000006": {
        "brightness": Around(0.5),
        "cap": [
            "color",
            "multizone",
            "not_chain",
            "not_ir",
            "variable_color_temp"
        ],
        "firmware_version": "1.1",
        "group_id": mock.ANY,
        "group_name": "desk",
        "hue": Around(200),
        "kelvin": 3500,
        "label": "tv",
        "location_id": mock.ANY,
        "location_name": "Work",
        "power": "on",
        "product_id": 31,
        "product_identifier": "lifx_z",
        "saturation": Around(0.5),
        "serial": "d073d5000006"
    }
}

light_state_responses = {
    "results": {
        "d073d5000001": {
            "payload": {
                "brightness": 1.0,
                "hue": 0.0,
                "kelvin": 3500,
                "label": "kitchen",
                "power": 0,
                "saturation": 1.0
            },
            "pkt_name": "LightState",
            "pkt_type": 107
        },
        "d073d5000002": {
            "payload": {
                "brightness": 1.0,
                "hue": Around(100),
                "kelvin": 3500,
                "label": "bathroom",
                "power": 65535,
                "saturation": 1.0
            },
            "pkt_name": "LightState",
            "pkt_type": 107
        },
        "d073d5000003": {
            "payload": {
                "brightness": 1.0,
                "hue": Around(100),
                "kelvin": 3500,
                "label": "lamp",
                "power": 65535,
                "saturation": 0.0
            },
            "pkt_name": "LightState",
            "pkt_type": 107
        },
        "d073d5000004": {
            "payload": {
                "brightness": 1.0,
                "hue": Around(100),
                "kelvin": 3500,
                "label": "lamp",
                "power": 65535,
                "saturation": 0.0
            },
            "pkt_name": "LightState",
            "pkt_type": 107
        },
        "d073d5000005": {
            "payload": {
                "brightness": Around(0.5),
                "hue": Around(200),
                "kelvin": 3500,
                "label": "desk",
                "power": 65535,
                "saturation": Around(0.5)
            },
            "pkt_name": "LightState",
            "pkt_type": 107
        },
        "d073d5000006": {
            "payload": {
                "brightness": Around(0.5),
                "hue": Around(200),
                "kelvin": 3500,
                "label": "tv",
                "power": 65535,
                "saturation": Around(0.5)
            },
            "pkt_name": "LightState",
            "pkt_type": 107
        }
    }
}

label_state_responses = {
    "results": {
        "d073d5000001": {
            "payload": {
                "label": "kitchen"
            },
            "pkt_name": "StateLabel",
            "pkt_type": 25
        },
        "d073d5000002": {
            "payload": {
                "label": "bathroom"
            },
            "pkt_name": "StateLabel",
            "pkt_type": 25
        },
        "d073d5000003": {
            "payload": {
                "label": "lamp"
            },
            "pkt_name": "StateLabel",
            "pkt_type": 25
        },
        "d073d5000004": {
            "payload": {
                "label": "lamp"
            },
            "pkt_name": "StateLabel",
            "pkt_type": 25
        },
        "d073d5000005": {
            "payload": {
                "label": "desk"
            },
            "pkt_name": "StateLabel",
            "pkt_type": 25
        },
        "d073d5000006": {
            "payload": {
                "label": "tv"
            },
            "pkt_name": "StateLabel",
            "pkt_type": 25
        }
    }
}

multizone_state_responses = {
    "results": {
        "d073d5000005": [
            {
                "payload": {
                    "colors": [
                        {
                            "brightness": 1.0,
                            "hue": 0.0,
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(10),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(20),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(30),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(40),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(50),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(60),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(70),
                            "kelvin": 2500,
                            "saturation": 1.0
                        }
                    ],
                    "num_zones": 16,
                    "zone_index": 0
                },
                "pkt_name": "StateMultiZoneStateMultiZones",
                "pkt_type": 506
            },
            {
                "payload": {
                    "colors": [
                        {
                            "brightness": 1.0,
                            "hue": Around(80),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(90),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(100),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(110),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(120),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(130),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(140),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(150),
                            "kelvin": 2500,
                            "saturation": 1.0
                        }
                    ],
                    "num_zones": 16,
                    "zone_index": 8
                },
                "pkt_name": "StateMultiZoneStateMultiZones",
                "pkt_type": 506
            }
        ],
        "d073d5000006": [
            {
                "payload": {
                    "colors": [
                        {
                            "brightness": 1.0,
                            "hue": 0.0,
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(10),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(20),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(30),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(40),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(50),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(60),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(70),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                    ],
                    "num_zones": 16,
                    "zone_index": 0
                },
                "pkt_name": "StateMultiZoneStateMultiZones",
                "pkt_type": 506
            },
            {
                "payload": {
                    "colors": [
                        {
                            "brightness": 1.0,
                            "hue": Around(80),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(90),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(100),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(110),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(120),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(130),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(140),
                            "kelvin": 2500,
                            "saturation": 1.0
                        },
                        {
                            "brightness": 1.0,
                            "hue": Around(150),
                            "kelvin": 2500,
                            "saturation": 1.0
                        }
                    ],
                    "num_zones": 16,
                    "zone_index": 8
                },
                "pkt_name": "StateMultiZoneStateMultiZones",
                "pkt_type": 506
            }
        ]
    }
}

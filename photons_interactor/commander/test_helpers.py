from photons_transport.fake import FakeDevice, Responder
from photons_control import test_helpers as chp
from photons_messages import DeviceMessages
from photons_products import Products

from delfick_project.norms import dictobj
from unittest import mock
import uuid


class Collection(dictobj):
    fields = ["uuid", "label", "updated_at"]


class CollectionResponder(Responder):
    _fields = ["group", "location"]

    async def respond(self, device, pkt, source):
        if pkt | DeviceMessages.GetGroup:
            yield DeviceMessages.StateGroup(
                group=device.attrs.group.uuid,
                label=device.attrs.group.label,
                updated_at=device.attrs.group.updated_at,
            )

        elif pkt | DeviceMessages.GetLocation:
            yield DeviceMessages.StateLocation(
                location=device.attrs.location.uuid,
                label=device.attrs.location.label,
                updated_at=device.attrs.location.updated_at,
            )


identifier = lambda: str(uuid.uuid4()).replace("-", "")
group_one = Collection(identifier(), "Living Room", 0)
group_two = Collection(identifier(), "Bathroom", 0)
location_one = Collection(identifier(), "Home", 0)
location_two = Collection(identifier(), "Work", 0)
group_three = Collection(identifier(), "desk", 0)

zones = []
for i in range(16):
    zones.append(chp.Color(i * 10, 1, 1, 2500))


class FakeDevice(FakeDevice):
    def compare_received_set(self, expected, keep_duplicates=False):
        self.received = [m for m in self.received if m.__class__.__name__.startswith("Set")]
        super().compare_received(expected, keep_duplicates=keep_duplicates)

    def expect_no_set_messages(self):
        assert not any([m for m in self.received if m.__class__.__name__.startswith("Set")])


a19_1 = FakeDevice(
    "d073d5000001",
    chp.default_responders(
        Products.LCM2_A19,
        label="kitchen",
        power=0,
        color=chp.Color(0, 1, 1, 2500),
        firmware=chp.Firmware(2, 75, 1521690429),
    )
    + [CollectionResponder(group=group_one, location=location_one)],
)

a19_2 = FakeDevice(
    "d073d5000002",
    chp.default_responders(
        Products.LCM2_A19,
        label="bathroom",
        power=65535,
        color=chp.Color(100, 1, 1, 2500),
        firmware=chp.Firmware(2, 75, 1521690429),
    )
    + [CollectionResponder(group=group_two, location=location_one)],
)

color1000 = FakeDevice(
    "d073d5000003",
    chp.default_responders(
        Products.LCMV4_A19_COLOR,
        label="lamp",
        power=65535,
        color=chp.Color(100, 0, 1, 2500),
        firmware=chp.Firmware(1, 1, 1530327089),
    )
    + [CollectionResponder(group=group_three, location=location_two)],
)

white800 = FakeDevice(
    "d073d5000004",
    chp.default_responders(
        Products.LCMV4_A19_WHITE_LV,
        label="lamp",
        power=65535,
        color=chp.Color(100, 0, 1, 2500),
        firmware=chp.Firmware(1, 1, 1530327089),
    )
    + [CollectionResponder(group=group_three, location=location_two)],
)

strip1 = FakeDevice(
    "d073d5000005",
    chp.default_responders(
        Products.LCM2_Z,
        label="desk",
        power=65535,
        zones=zones,
        color=chp.Color(200, 0.5, 0.5, 2500),
        firmware=chp.Firmware(2, 75, 1521690429),
    )
    + [CollectionResponder(group=group_one, location=location_one)],
)

strip2 = FakeDevice(
    "d073d5000006",
    chp.default_responders(
        Products.LCM1_Z,
        label="tv",
        power=65535,
        zones=zones,
        color=chp.Color(200, 0.5, 0.5, 2500),
        firmware=chp.Firmware(1, 1, 1530327089),
    )
    + [CollectionResponder(group=group_three, location=location_two)],
)

candle = FakeDevice(
    "d073d5000007",
    chp.default_responders(
        Products.LCM3_CANDLE,
        label="pretty",
        power=65535,
        firmware=chp.Firmware(3, 50, 1562659776000000000),
    )
    + [CollectionResponder(group=group_three, location=location_two)],
)


class Fakery:
    def __init__(self):
        self.devices = [a19_1, a19_2, color1000, white800, strip1, strip2, candle]

    def for_attribute(self, key, value, expect=1):
        got = []
        for d in self.devices:
            if d.attrs[key] == value:
                got.append(d)
        assert len(got) == expect, f"Expected {expect} devices, got {len(got)}: {got}"
        return got

    def for_serial(self, serial):
        for d in self.devices:
            if d.serial == serial:
                return d
        assert False, f"Expected one device with serial {serial}"


fakery = Fakery()


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
            "not_matrix",
            "not_multizone",
            "variable_color_temp",
        ],
        "firmware_version": "2.75",
        "group_id": mock.ANY,
        "group_name": "Living Room",
        "hue": 0.0,
        "kelvin": 2500,
        "label": "kitchen",
        "location_id": mock.ANY,
        "location_name": "Home",
        "power": "off",
        "product_id": 27,
        "product_identifier": "lifx_a19",
        "saturation": 1.0,
        "serial": "d073d5000001",
    },
    "d073d5000002": {
        "brightness": 1.0,
        "cap": [
            "color",
            "not_chain",
            "not_ir",
            "not_matrix",
            "not_multizone",
            "variable_color_temp",
        ],
        "firmware_version": "2.75",
        "group_id": mock.ANY,
        "group_name": "Bathroom",
        "hue": Around(100),
        "kelvin": 2500,
        "label": "bathroom",
        "location_id": mock.ANY,
        "location_name": "Home",
        "power": "on",
        "product_id": 27,
        "product_identifier": "lifx_a19",
        "saturation": 1.0,
        "serial": "d073d5000002",
    },
    "d073d5000003": {
        "brightness": 1.0,
        "cap": [
            "color",
            "not_chain",
            "not_ir",
            "not_matrix",
            "not_multizone",
            "variable_color_temp",
        ],
        "firmware_version": "1.1",
        "group_id": mock.ANY,
        "group_name": "desk",
        "hue": Around(100),
        "kelvin": 2500,
        "label": "lamp",
        "location_id": mock.ANY,
        "location_name": "Work",
        "power": "on",
        "product_id": 22,
        "product_identifier": "lifx_a19_color",
        "saturation": 0.0,
        "serial": "d073d5000003",
    },
    "d073d5000004": {
        "brightness": 1.0,
        "cap": [
            "not_chain",
            "not_color",
            "not_ir",
            "not_matrix",
            "not_multizone",
            "variable_color_temp",
        ],
        "firmware_version": "1.1",
        "group_id": mock.ANY,
        "group_name": "desk",
        "hue": Around(100),
        "kelvin": 2500,
        "label": "lamp",
        "location_id": mock.ANY,
        "location_name": "Work",
        "power": "on",
        "product_id": 10,
        "product_identifier": "lifx_a19_white",
        "saturation": 0.0,
        "serial": "d073d5000004",
    },
    "d073d5000005": {
        "brightness": Around(0.5),
        "cap": ["color", "multizone", "not_chain", "not_ir", "not_matrix", "variable_color_temp"],
        "firmware_version": "2.75",
        "group_id": mock.ANY,
        "group_name": "Living Room",
        "hue": Around(200),
        "kelvin": 2500,
        "label": "desk",
        "location_id": mock.ANY,
        "location_name": "Home",
        "power": "on",
        "product_id": 32,
        "product_identifier": "lifx_z",
        "saturation": Around(0.5),
        "serial": "d073d5000005",
    },
    "d073d5000006": {
        "brightness": Around(0.5),
        "cap": ["color", "multizone", "not_chain", "not_ir", "not_matrix", "variable_color_temp"],
        "firmware_version": "1.1",
        "group_id": mock.ANY,
        "group_name": "desk",
        "hue": Around(200),
        "kelvin": 2500,
        "label": "tv",
        "location_id": mock.ANY,
        "location_name": "Work",
        "power": "on",
        "product_id": 31,
        "product_identifier": "lifx_z",
        "saturation": Around(0.5),
        "serial": "d073d5000006",
    },
    "d073d5000007": {
        "brightness": 1.0,
        "cap": ["color", "matrix", "not_chain", "not_ir", "not_multizone", "variable_color_temp"],
        "firmware_version": "3.50",
        "group_id": mock.ANY,
        "group_name": "desk",
        "hue": 0.0,
        "kelvin": 3500,
        "label": "pretty",
        "location_id": mock.ANY,
        "location_name": "Work",
        "power": "on",
        "product_id": 57,
        "product_identifier": "lifx_candle",
        "saturation": 1.0,
        "serial": "d073d5000007",
    },
}

light_state_responses = {
    "results": {
        "d073d5000001": {
            "payload": {
                "brightness": 1.0,
                "hue": 0.0,
                "kelvin": 2500,
                "label": "kitchen",
                "power": 0,
                "saturation": 1.0,
            },
            "pkt_name": "LightState",
            "pkt_type": 107,
        },
        "d073d5000002": {
            "payload": {
                "brightness": 1.0,
                "hue": Around(100),
                "kelvin": 2500,
                "label": "bathroom",
                "power": 65535,
                "saturation": 1.0,
            },
            "pkt_name": "LightState",
            "pkt_type": 107,
        },
        "d073d5000003": {
            "payload": {
                "brightness": 1.0,
                "hue": Around(100),
                "kelvin": 2500,
                "label": "lamp",
                "power": 65535,
                "saturation": 0.0,
            },
            "pkt_name": "LightState",
            "pkt_type": 107,
        },
        "d073d5000004": {
            "payload": {
                "brightness": 1.0,
                "hue": Around(100),
                "kelvin": 2500,
                "label": "lamp",
                "power": 65535,
                "saturation": 0.0,
            },
            "pkt_name": "LightState",
            "pkt_type": 107,
        },
        "d073d5000005": {
            "payload": {
                "brightness": Around(0.5),
                "hue": Around(200),
                "kelvin": 2500,
                "label": "desk",
                "power": 65535,
                "saturation": Around(0.5),
            },
            "pkt_name": "LightState",
            "pkt_type": 107,
        },
        "d073d5000006": {
            "payload": {
                "brightness": Around(0.5),
                "hue": Around(200),
                "kelvin": 2500,
                "label": "tv",
                "power": 65535,
                "saturation": Around(0.5),
            },
            "pkt_name": "LightState",
            "pkt_type": 107,
        },
        "d073d5000007": {
            "payload": {
                "brightness": 1.0,
                "hue": 0.0,
                "kelvin": 3500,
                "label": "pretty",
                "power": 65535,
                "saturation": 1.0,
            },
            "pkt_name": "LightState",
            "pkt_type": 107,
        },
    }
}

label_state_responses = {
    "results": {
        "d073d5000001": {"payload": {"label": "kitchen"}, "pkt_name": "StateLabel", "pkt_type": 25},
        "d073d5000002": {
            "payload": {"label": "bathroom"},
            "pkt_name": "StateLabel",
            "pkt_type": 25,
        },
        "d073d5000003": {"payload": {"label": "lamp"}, "pkt_name": "StateLabel", "pkt_type": 25},
        "d073d5000004": {"payload": {"label": "lamp"}, "pkt_name": "StateLabel", "pkt_type": 25},
        "d073d5000005": {"payload": {"label": "desk"}, "pkt_name": "StateLabel", "pkt_type": 25},
        "d073d5000006": {"payload": {"label": "tv"}, "pkt_name": "StateLabel", "pkt_type": 25},
        "d073d5000007": {"payload": {"label": "pretty"}, "pkt_name": "StateLabel", "pkt_type": 25},
    }
}

multizone_state_responses = {
    "results": {
        "d073d5000005": [
            {
                "payload": {
                    "colors": [
                        {"brightness": 1.0, "hue": 0.0, "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(10), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(20), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(30), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(40), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(50), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(60), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(70), "kelvin": 2500, "saturation": 1.0},
                    ],
                    "zones_count": 16,
                    "zone_index": 0,
                },
                "pkt_name": "StateMultiZone",
                "pkt_type": 506,
            },
            {
                "payload": {
                    "colors": [
                        {"brightness": 1.0, "hue": Around(80), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(90), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(100), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(110), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(120), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(130), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(140), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(150), "kelvin": 2500, "saturation": 1.0},
                    ],
                    "zones_count": 16,
                    "zone_index": 8,
                },
                "pkt_name": "StateMultiZone",
                "pkt_type": 506,
            },
        ],
        "d073d5000006": [
            {
                "payload": {
                    "colors": [
                        {"brightness": 1.0, "hue": 0.0, "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(10), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(20), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(30), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(40), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(50), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(60), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(70), "kelvin": 2500, "saturation": 1.0},
                    ],
                    "zones_count": 16,
                    "zone_index": 0,
                },
                "pkt_name": "StateMultiZone",
                "pkt_type": 506,
            },
            {
                "payload": {
                    "colors": [
                        {"brightness": 1.0, "hue": Around(80), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(90), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(100), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(110), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(120), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(130), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(140), "kelvin": 2500, "saturation": 1.0},
                        {"brightness": 1.0, "hue": Around(150), "kelvin": 2500, "saturation": 1.0},
                    ],
                    "zones_count": 16,
                    "zone_index": 8,
                },
                "pkt_name": "StateMultiZone",
                "pkt_type": 506,
            },
        ],
    }
}

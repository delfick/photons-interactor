# coding: spec

from photons_interactor.commander import helpers as chp

from photons_app.errors import PhotonsAppError
from photons_app.test_helpers import TestCase

from photons_messages import DeviceMessages

import types

class ATraceback:
    def __eq__(self, other):
        return isinstance(other, types.TracebackType)

describe TestCase, "ResultBuilder":
    it "initializes itself":
        builder = chp.ResultBuilder(["one", "two"])
        self.assertEqual(builder.serials, ["one", "two"])
        self.assertEqual(builder.result, {"results": {}})
        self.assertEqual(builder.exc_info, {})

    it "can add serials":
        builder = chp.ResultBuilder(["one", "two"])
        self.assertEqual(builder.serials, ["one", "two"])

        builder.add_serials(["three", "two", "four"])
        self.assertEqual(builder.serials, ["one", "two", "three", "four"])

    describe "as_dict":
        it "returns results but with ok for devices":
            builder = chp.ResultBuilder(["one", "two"])
            dct = builder.as_dict()
            self.assertEqual(builder.result, {"results": {}})
            self.assertEqual(dct, {"results": {"one": "ok", "two": "ok"}})

        it "doesn't give ok for devices that already have results":
            builder = chp.ResultBuilder(["one", "two", "three"])
            builder.result["results"]["one"] = {"pkt_type": 1}
            builder.result["results"]["three"] = {"error": "blah"}
            dct = builder.as_dict()

            self.assertEqual(builder.result, {"results": {"one": {"pkt_type": 1}, "three": {"error": "blah"}}})
            self.assertEqual(dct, {"results": {"one": {"pkt_type": 1}, "two": "ok", "three": {"error": "blah"}}})

        it "includes errors on result":
            builder = chp.ResultBuilder(["one", "two"])
            builder.result["errors"] = ["error1", "error2"]
            dct = builder.as_dict()

            self.assertEqual(builder.result, {"results": {}, "errors": ["error1", "error2"]})
            self.assertEqual(dct, {"results": {"one": "ok", "two": "ok"}, "errors": ["error1", "error2"]})

    describe "add_packet":
        it "sets info for that serial in results":
            packet = DeviceMessages.StatePower(level=0, target="d073d5000001")
            info = {"pkt_type": 22, "pkt_name": "StatePower", "payload": {"level": 0}}
            builder = chp.ResultBuilder(["d073d5000001"])
            builder.add_packet(packet)

            self.assertEqual(builder.as_dict(), {"results": {"d073d5000001": info}})

        it "makes a list if already have packet for that bulb":
            packet1 = DeviceMessages.StatePower(level=0, target="d073d5000001")
            packet2 = DeviceMessages.StatePower(level=65535, target="d073d5000001")
            packet3 = DeviceMessages.StateHostFirmware(build=0, version="1.2", target="d073d5000001")

            info1 = {"pkt_type": 22, "pkt_name": "StatePower", "payload": {"level": 0}}
            info2 = {"pkt_type": 22, "pkt_name": "StatePower", "payload": {"level": 65535}}
            info3 = {"pkt_type": 15, "pkt_name": "StateHostFirmware", "payload": {"build": 0, "version": "1.2"}}

            builder = chp.ResultBuilder(["d073d5000001"])
            builder.add_packet(packet1)
            self.assertEqual(builder.as_dict(), {"results": {"d073d5000001": info1}})

            builder.add_packet(packet2)
            self.assertEqual(builder.as_dict(), {"results": {"d073d5000001": [info1, info2]}})

            builder.add_packet(packet3)
            self.assertEqual(builder.as_dict(), {"results": {"d073d5000001": [info1, info2, info3]}})

    describe "error":
        it "adds the error for that serial if we can get serial from the error":
            builder = chp.ResultBuilder(["d073d5000001"])

            class BadError(PhotonsAppError):
                pass
            error = BadError("blah", serial="d073d5000001")
            builder.error(error)
            self.assertEqual(builder.as_dict()
                , { "results":
                    { "d073d5000001": {"error": {"message": "blah"}, "error_code": "BadError", "status": 400}
                    }
                  }
                )
            self.assertEqual(builder.exc_info, {"d073d5000001": (BadError, error, None)})

            class Error(PhotonsAppError):
                desc = "an error"

            error2 = None

            try:
                raise Error("wat", thing=1, serial="d073d5000001")
            except Exception as error:
                error2 = error

            builder.error(error2)
            self.assertEqual(builder.as_dict()
                , { "results":
                    { "d073d5000001":
                      { "error": {"message": "an error. wat", "thing": 1}
                      , "error_code": "Error"
                      , "status": 400
                      }
                    }
                  }
                )
            self.assertEqual(builder.exc_info, {"d073d5000001": (Error, error2, ATraceback())})

        it "adds error to errors in result if no serial on the error":
            builder = chp.ResultBuilder(["d073d5000001"])

            error = PhotonsAppError("blah")
            builder.error(error)
            self.assertEqual(builder.as_dict()
                , { "results": {"d073d5000001": "ok"}
                  , "errors":
                  [ {"error": {"message": "blah"}, "error_code": "PhotonsAppError", "status": 400}
                    ]
                  }
                )
            self.assertEqual(builder.exc_info, {None: [(PhotonsAppError, error, None)]})

            class Error(PhotonsAppError):
                desc = "an error"

            error2 = None
            try:
                raise Error("wat", thing=1)
            except Exception as e:
                error2 = e

            builder.error(error2)
            self.assertEqual(builder.as_dict()
                , { "results":
                    { "d073d5000001": "ok"
                    }
                  , "errors":
                  [ {"error": {"message": "blah"}, "error_code": "PhotonsAppError", "status": 400}
                      , {"error": {"message": "an error. wat", "thing": 1}, "error_code": "Error", "status": 400}
                    ]
                  }
                )
            self.assertEqual(builder.exc_info
                , { None:
                    [ (PhotonsAppError, error, None)
                    , (Error, error2, ATraceback())
                    ]
                  }
                )

            builder = chp.ResultBuilder(["d073d5000001"])
            error3 = ValueError("nope")
            builder.error(error3)
            self.assertEqual(builder.as_dict()
                , { "results": {"d073d5000001": "ok"}
                  , "errors":
                  [ {"error": "Internal Server Error", "error_code": "InternalServerError", "status": 500}
                    ]
                  }
                )
            self.assertEqual(builder.exc_info, {None: [(ValueError, error3, None)]})

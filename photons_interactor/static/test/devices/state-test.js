import { WSCommand } from "../../js/wsclient.js";
import { makeReducer } from "../../js/store.js";
import { makeTestStore } from "../helpers.js";
import {
  DevicesState,
  deviceSaga,
  fortests as devicemod
} from "../../js/device/state.js";

import { put, takeLatest } from "redux-saga/effects";
import { assert } from "chai";

describe("Devices Sagas", () => {
  describe("deviceSaga", () => {
    it("converts some commands", () => {
      var saga = deviceSaga();
      assert.deepEqual(
        saga.next().value,
        takeLatest(DevicesState.GetSerials, devicemod.getSerialsSaga)
      );
      assert.deepEqual(
        saga.next().value,
        takeLatest(DevicesState.GotSerials, devicemod.gotSerialsSaga)
      );
      assert.deepEqual(
        saga.next().value,
        takeLatest(DevicesState.GetDetails, devicemod.getDetailsSaga)
      );
      assert.deepEqual(
        saga.next().value,
        takeLatest(DevicesState.Refresh, devicemod.refreshSaga)
      );
      assert(saga.next().done);
    });
  });

  const getWSCommand = (saga, original) => {
    var saga = saga(original);
    var result = saga.next().value;
    var payload = result.PUT.action.payload;
    delete result.PUT.action.payload;

    var want = WSCommand("<path>", undefined, {});
    delete want.payload;

    assert.deepEqual(result, put(want));
    assert(saga.next().done);

    return payload;
  };

  describe("getSerialsSaga", () => {
    it("creates a WSCommand", () => {
      var original = DevicesState.GetSerials();
      var payload = getWSCommand(devicemod.getSerialsSaga, original);

      assert.deepEqual(payload.path, "/v1/lifx/command");
      assert.deepEqual(payload.body, {
        command: "discover",
        args: { just_serials: true, refresh: false }
      });

      var serials = ["d1", "d2"];
      assert.deepEqual(
        payload.onsuccess({ data: serials }),
        DevicesState.GotSerials({ serials })
      );
      assert.deepEqual(payload.onerror, DevicesState.DetailsError);

      assert.deepEqual(payload.original, original);
    });

    it("takes into account refresh and other args", () => {
      var original = DevicesState.GetSerials(true, { one: 1 });
      var payload = getWSCommand(devicemod.getSerialsSaga, original);

      assert.deepEqual(payload.path, "/v1/lifx/command");
      assert.deepEqual(payload.body, {
        command: "discover",
        args: { just_serials: true, refresh: true, one: 1 }
      });
    });
  });

  describe("getDetailsSaga", () => {
    it("creates a WSCommand", () => {
      var original = DevicesState.GetDetails();
      var payload = getWSCommand(devicemod.getDetailsSaga, original);

      assert.deepEqual(payload.path, "/v1/lifx/command");
      assert.deepEqual(payload.body, {
        command: "discover",
        args: { refresh: false }
      });

      var devices = { d1: { one: 1 }, d2: { two: 2 } };
      assert.deepEqual(
        payload.onsuccess({ data: devices }),
        DevicesState.GotDetails({ devices })
      );
      assert.deepEqual(payload.onerror, DevicesState.DetailsError);

      assert.deepEqual(payload.original, original);
    });

    it("takes into account refresh", () => {
      var original = DevicesState.GetDetails(true, { four: 4 });
      var payload = getWSCommand(devicemod.getDetailsSaga, original);

      assert.deepEqual(payload.path, "/v1/lifx/command");
      assert.deepEqual(payload.body, {
        command: "discover",
        args: { refresh: true, four: 4 }
      });
    });
  });

  describe("gotSerialsSaga", () => {
    it("asks for a GetDetails()", () => {
      var original = DevicesState.Refresh();
      var saga = devicemod.gotSerialsSaga(original);
      var result = saga.next().value;
      var payload = result.PUT.action;
      assert.deepEqual(payload, DevicesState.GetDetails());
      assert(saga.next().done);
    });
  });

  describe("refreshSaga", () => {
    it("asks for a GetDetails(refresh)", () => {
      var original = DevicesState.Refresh();
      var saga = devicemod.refreshSaga(original);
      var result = saga.next().value;
      var payload = result.PUT.action;
      assert.deepEqual(payload, DevicesState.GetDetails(true));
      assert(saga.next().done);
    });
  });
});

describe("DevicesState", () => {
  describe("Actions", () => {
    describe("GetSerials", () => {
      it("defaults payload to have args", () => {
        var action = DevicesState.GetSerials();
        assert.deepEqual(action.payload, {
          args: { just_serials: true, refresh: false }
        });
      });

      it("understands refresh", () => {
        var action = DevicesState.GetSerials(true);
        assert.deepEqual(action.payload, {
          args: { just_serials: true, refresh: true }
        });
      });

      it("can take in other args", () => {
        var action = DevicesState.GetSerials(true, { one: 1 });
        assert.deepEqual(action.payload, {
          args: { just_serials: true, refresh: true, one: 1 }
        });
      });

      it("doesn't allow args to override just_serials or refresh", () => {
        var action = DevicesState.GetSerials(true, {
          just_serials: false,
          refresh: false,
          two: 2
        });
        assert.deepEqual(action.payload, {
          args: { just_serials: true, refresh: true, two: 2 }
        });
      });
    });

    describe("GetDetails", () => {
      it("defaults payload to have args", () => {
        var action = DevicesState.GetDetails();
        assert.deepEqual(action.payload, {
          args: { refresh: false }
        });
      });

      it("understands refresh", () => {
        var action = DevicesState.GetDetails(true);
        assert.deepEqual(action.payload, {
          args: { refresh: true }
        });
      });

      it("can take in other args", () => {
        var action = DevicesState.GetDetails(true, { one: 1 });
        assert.deepEqual(action.payload, {
          args: { refresh: true, one: 1 }
        });
      });

      it("doesn't allow args to override refresh", () => {
        var action = DevicesState.GetDetails(true, {
          refresh: false,
          two: 2
        });
        assert.deepEqual(action.payload, {
          args: { refresh: true, two: 2 }
        });
      });
    });
  });

  describe("store", () => {
    it("has default state", () => {
      var { store } = makeTestStore(makeReducer());
      var { devices } = store.getState();
      assert.deepEqual(devices, {
        devices: {},
        error: undefined,
        loading: true,
        serials: []
      });
    });

    it("responds to GotSerials", () => {
      var { store } = makeTestStore(makeReducer());
      var serials = ["d1", "d2"];
      store.dispatch(DevicesState.GotSerials({ serials }));
      var { devices } = store.getState();
      assert.deepEqual(devices.serials, serials);
      assert.deepEqual(devices.loading, false);
    });

    it("responds to GotDetails", () => {
      var { store } = makeTestStore(makeReducer());
      var devices = { d1: { one: 1 }, d2: { two: 2 } };
      store.dispatch(DevicesState.GotDetails({ devices }));
      var state = store.getState();
      assert.deepEqual(state.devices.devices, devices);
      assert.deepEqual(state.devices.loading, false);
    });

    it("updates serials if different in the  GotDetails", () => {
      var { store } = makeTestStore(makeReducer());
      var serials = ["d1"];
      store.dispatch(DevicesState.GotSerials({ serials }));
      var state = store.getState();
      assert.deepEqual(state.devices.serials, ["d1"]);

      var devices = { d1: { one: 1 }, d2: { two: 2 } };
      store.dispatch(DevicesState.GotDetails({ devices }));
      var state = store.getState();
      assert.deepEqual(state.devices.devices, devices);
      assert.deepEqual(state.devices.loading, false);
      assert.deepEqual(state.devices.serials, ["d1", "d2"]);
    });

    it("responds to DetailsError and ClearError", () => {
      var { store } = makeTestStore(makeReducer());
      var error = { error: "well that didn't work", error_code: "NoWorky" };
      store.dispatch(DevicesState.DetailsError(error));
      var { devices } = store.getState();
      assert.deepEqual(devices.error, 'NoWorky: "well that didn\'t work"');
      assert.deepEqual(devices.loading, false);

      store.dispatch(DevicesState.ClearError());
      var { devices } = store.getState();
      assert.deepEqual(devices.error, undefined);
    });
  });
});

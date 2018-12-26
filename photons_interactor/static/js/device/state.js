import { WSCommand } from "../wsclient.js";

import { take, put, takeLatest } from "redux-saga/effects";
import { createAction, createReducer } from "redux-act";

class DevicesStateKls {
  GetSerials = createAction("Get serials", (refresh, other_args) => ({
    args: { ...other_args, just_serials: true, refresh: refresh || false }
  }));
  GotSerials = createAction("Got serials");

  GetDetails = createAction("Get details", (refresh, other_args) => ({
    args: { ...other_args, refresh: refresh || false }
  }));
  GotDetails = createAction("Got details");

  Refresh = createAction("Refresh devices");

  DetailsError = createAction("Error getting information");
  ClearError = createAction("Clear the error");

  reducer() {
    return createReducer(
      {
        [this.GotSerials]: (state, { serials }) => {
          return { ...state, serials, loading: false };
        },
        [this.GotDetails]: (state, { devices }) => {
          return {
            ...state,
            devices: devices || {},
            serials: Object.keys(devices).sort(),
            loading: false
          };
        },
        [this.Refresh]: (state, payload) => {
          return {
            ...state,
            serials: [],
            devices: {},
            loading: true
          };
        },
        [this.DetailsError]: (state, { error, error_code }) => {
          var errormsg = `${error_code}: ${JSON.stringify(error)}`;
          return { ...state, error: errormsg, loading: false };
        },
        [this.ClearError]: (state, payload) => {
          return { ...state, error: undefined };
        }
      },
      {
        serials: [],
        error: undefined,
        devices: {},
        loading: true
      }
    );
  }
}

export const DevicesState = new DevicesStateKls();

function* getDetailsSaga(original) {
  var { payload } = original;
  var onsuccess = ({ data }) => DevicesState.GotDetails({ devices: data });
  var onerror = DevicesState.DetailsError;

  yield put(
    WSCommand(
      "/v1/lifx/command",
      {
        command: "discover",
        args: payload.args
      },
      { onsuccess, onerror, original }
    )
  );
}

function* getSerialsSaga(original) {
  var { payload } = original;
  var onsuccess = ({ data }) => DevicesState.GotSerials({ serials: data });
  var onerror = DevicesState.DetailsError;

  yield put(
    WSCommand(
      "/v1/lifx/command",
      {
        command: "discover",
        args: { ...payload.args, just_serials: true }
      },
      { onsuccess, onerror, original }
    )
  );
}

function* gotSerialsSaga(original) {
  yield put(DevicesState.GetDetails());
}

function* refreshSaga(original) {
  yield put(DevicesState.GetDetails(true));
}

export function* deviceSaga() {
  yield takeLatest(DevicesState.GetSerials, getSerialsSaga);
  yield takeLatest(DevicesState.GotSerials, gotSerialsSaga);
  yield takeLatest(DevicesState.GetDetails, getDetailsSaga);
  yield takeLatest(DevicesState.Refresh, refreshSaga);
}

export const fortests = {
  getDetailsSaga,
  getSerialsSaga,
  gotSerialsSaga,
  refreshSaga
};

import { createAction, createReducer } from "redux-act";
import { take, put, takeLatest } from "redux-saga/effects";

import { WSCommand } from "./wsclient.js";

class DevicesStateKls {
  GetSerials = createAction("Get serials", refresh => ({
    args: { just_serials: true, refresh: refresh || false }
  }));
  GotSerials = createAction("Got serials");

  GetDetails = createAction("Get details", refresh => ({
    args: { refresh: refresh || false }
  }));
  GotDetails = createAction("Got details");

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
            loading: false
          };
        },
        [this.DetailsError]: (state, { error }) => {
          var errormsg = `${error.error_code}: ${JSON.stringify(error.error)}`;
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

function* getDetailsSaga({ payload }) {
  var onsuccess = ({ data }) => DevicesState.GotDetails({ devices: data });
  var onerror = DevicesState.DetailsError;

  yield put(
    WSCommand(
      "/v1/lifx/command",
      {
        command: "discover",
        args: payload.args
      },
      { onsuccess, onerror }
    )
  );
}

function* getSerialsSaga({ payload }) {
  var onsuccess = ({ data }) => DevicesState.GotSerials({ serials: data });
  var onerror = DevicesState.DetailsError;

  yield put(
    WSCommand(
      "/v1/lifx/command",
      {
        command: "discover",
        args: { ...payload.args, just_serials: true }
      },
      { onsuccess, onerror }
    )
  );
}

export function* deviceSaga() {
  yield takeLatest(DevicesState.GetSerials, getSerialsSaga);
  yield takeLatest(DevicesState.GetDetails, getDetailsSaga);
}

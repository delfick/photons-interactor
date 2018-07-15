import { WSCommand } from "../wsclient.js";

import { take, put, takeLatest, select } from "redux-saga/effects";
import { createAction, createReducer } from "redux-act";

class SelectionStateKls {
  SetPower = createAction("Set power", power => ({
    transform: { power: power ? "on" : "off" }
  }));

  ToggleSelection = createAction("Toggle a selection");
  StateChangeError = createAction("Error changing state");

  ClearError = createAction("Clear error");

  reducer() {
    return createReducer(
      {
        [this.ToggleSelection]: (state, { serial }) => {
          var selection = { ...state.selection };
          if (selection[serial]) {
            delete selection[serial];
          } else {
            selection[serial] = true;
          }
          return { ...state, selection };
        },
        [this.StateChangeError]: (state, { error }) => {
          var errormsg = `${error.error_code}: ${JSON.stringify(error.error)}`;
          return { ...state, error: errormsg };
        },
        [this.ClearError]: (state, payload) => {
          return { ...state, error: undefined };
        }
      },
      {
        selection: {},
        error: undefined
      }
    );
  }
}

export const SelectionState = new SelectionStateKls();

function* setPowerSaga(original) {
  var { payload } = original;
  var onerror = SelectionState.StateChangeError;

  var state = yield select();
  var selection = state.selection.selection;
  var matcher = { serial: Object.keys(selection) };

  yield put(
    WSCommand(
      "/v1/lifx/command",
      {
        command: "transform",
        args: { matcher, transform: payload.transform }
      },
      { onerror, original }
    )
  );
}

export function* selectionSaga() {
  yield takeLatest(SelectionState.SetPower, setPowerSaga);
}

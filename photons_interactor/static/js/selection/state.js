import { WSCommand } from "../wsclient.js";

import { take, put, takeLatest, select, call } from "redux-saga/effects";
import { createAction, createReducer } from "redux-act";
import { delay } from "redux-saga";

class SelectionStateKls {
  SetPower = createAction("Set power", power => ({
    transform: { power: power ? "on" : "off" }
  }));

  ChangeState = createAction("Change state", (transform, components) => ({
    transform,
    components
  }));

  GotState = createAction("Got state from a light");

  StartWaiting = createAction("Start waiting");
  StopWaiting = createAction("Stop waiting");

  ToggleWheel = createAction("Toggle the wheel", white => ({ white }));

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
          return {
            ...state,
            selection,
            state_number: state.state_number + 1,
            waiting: Object.keys(selection) === 0,
            light_state: { ...state.light_state, ...state.light_state_buf }
          };
        },
        [this.StartWaiting]: (state, payload) => {
          return { ...state, waiting: true };
        },
        [this.StopWaiting]: (state, { state_number }) => {
          var waiting = state.waiting;
          if (state_number === state.state_number) {
            waiting = false;
          }
          return {
            ...state,
            waiting,
            state_number: state.state_number + 1
          };
        },
        [this.ToggleWheel]: (state, { white }) => {
          return {
            ...state,
            white,
            light_state: { ...state.light_state, ...state.light_state_buf }
          };
        },
        [this.GotState]: (state, { state_number, serial, data }) => {
          if (state.state_number !== state_number) {
            return state;
          }

          var serials = Object.keys(state.selection);
          if (serials.length !== 1 || serials[0] !== serial) {
            return state;
          }

          return {
            ...state,
            light_state: data,
            light_state_buf: data,
            waiting: false
          };
        },
        [this.StateChangeError]: (state, { error, error_code }) => {
          var errormsg = `${error_code}: ${JSON.stringify(error)}`;
          return { ...state, error: errormsg };
        },
        [this.ClearError]: (state, payload) => {
          return { ...state, error: undefined };
        },
        [this.ChangeState]: (state, { components }) => {
          return {
            ...state,
            state_number: state.state_number + 1,
            light_state_buf: { ...state.light_state_buf, ...components }
          };
        }
      },
      {
        selection: {},
        error: undefined,
        light_state_buf: {},
        state_number: 0,
        white: false,
        waiting: false,
        light_state: {
          on: true,
          hue: 0,
          saturation: 1,
          brightness: 0.5,
          kelvin: 3500
        }
      }
    );
  }
}

export const SelectionState = new SelectionStateKls();

function* setTransformSaga(original) {
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

function* askForDetailsSaga(original) {
  var state = yield select();
  var selection = Object.keys(state.selection.selection);
  if (selection.length !== 1) {
    return;
  }

  var serial = selection[0];
  yield put(SelectionState.StartWaiting());

  var state = yield select();
  var state_number = state.selection.state_number;

  var onsuccess = ({ data }) => {
    var results = data.results[serial];
    if (results) {
      var payload = results.payload;
      var { hue, saturation, brightness, kelvin } = payload;
      var data = {
        on: payload.power !== 0,
        hue,
        saturation,
        brightness,
        kelvin
      };
      return SelectionState.GotState({ data, serial, state_number });
    }
  };

  var onerror = ({ error }) => console.error(error);

  yield put(
    WSCommand(
      "/v1/lifx/command",
      {
        command: "query",
        args: { matcher: { serial }, pkt_type: "GetColor" }
      },
      { onerror, onsuccess, original }
    )
  );

  yield call(delay, 1000);
  yield put(SelectionState.StopWaiting({ state_number }));
}

export function* selectionSaga() {
  yield takeLatest(
    [SelectionState.SetPower, SelectionState.ChangeState],
    setTransformSaga
  );
  yield takeLatest(SelectionState.ToggleSelection, askForDetailsSaga);
}

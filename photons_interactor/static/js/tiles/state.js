import { WSCommand } from "../wsclient.js";

import { select, put, takeLatest } from "redux-saga/effects";
import { createAction, createReducer } from "redux-act";

export const DisplayDice = createAction(
  "Display dice on a tile",
  (serial, onFinish) => {
    if (onFinish === undefined) {
      throw new Error("onFinish cannot be undefined");
    }
    return {
      serial,
      onFinish
    };
  }
);

class AnimationsStateKls {
  EnsureStatusStream = createAction(
    "Ensure we have a stream to animation status"
  );
  LostStatusStream = createAction("We lost the status stream");

  GotStatus = createAction("Got status from the stream", status => ({
    status
  }));

  GotAvailableAnimations = createAction(
    "Got available animations",
    available => ({ available })
  );

  PauseAnimation = createAction("Pause an animation", animation_id => ({
    animation_id
  }));

  ResumeAnimation = createAction("Resume an animation", animation_id => ({
    animation_id
  }));

  RemoveAnimation = createAction("Remove an animation", animation_id => ({
    animation_id
  }));

  StartAnimation = createAction("Start an animation", (matcher, animation) => ({
    matcher,
    animation
  }));

  reducer() {
    return createReducer(
      {
        [this.LostStatusStream]: (state, payload) => {
          return { ...state, gettingstatus: false };
        },
        [WSCommand]: (state, payload) => {
          var gettingstatus = state.gettingstatus;
          if (
            payload.path === "/v1/lifx/command" &&
            payload.body &&
            payload.body.command === "animate/status_stream"
          ) {
            gettingstatus = true;
          }
          return { ...state, gettingstatus };
        },
        [this.GotStatus]: (state, { status }) => {
          var { running_animations, statuses } = status;
          return { ...state, running_animations, statuses };
        },
        [this.GotAvailableAnimations]: (state, { available }) => {
          return { ...state, available };
        }
      },
      {
        statuses: {},
        available: [],
        gettingstatus: false,
        running_animations: 0
      }
    );
  }
}

export const AnimationsState = new AnimationsStateKls();

function* lostStatusStreamSaga(original) {
  var onerror = AnimationsState.LostStatusStream;
  var onsuccess = AnimationsState.EnsureStatusStream;

  yield put(
    WSCommand(
      "/v1/lifx/command",
      {
        command: "status"
      },
      { onsuccess, onerror, original }
    )
  );
}

function* ensureStatusSaga(original) {
  var onprogress = ({ progress }) => {
    if (progress.available) {
      return AnimationsState.GotAvailableAnimations(progress.available);
    } else {
      return AnimationsState.GotStatus(progress.status);
    }
  };

  var onerror = e => {
    console.error(e);
    return AnimationsState.LostStatusStream();
  };

  var state = yield select();
  if (state.animations.gettingstatus) {
    return;
  }

  yield put(
    WSCommand(
      "/v1/lifx/command",
      {
        command: "animate/status_stream"
      },
      { onprogress, onerror, original }
    )
  );
}

function* pauseAnimationSaga(original) {
  yield put(
    WSCommand(
      "/v1/lifx/command",
      { command: "animate/pause", args: original.payload },
      { original }
    )
  );
}

function* resumeAnimationSaga(original) {
  yield put(
    WSCommand(
      "/v1/lifx/command",
      { command: "animate/resume", args: original.payload },
      { original }
    )
  );
}

function* startAnimationSaga(original) {
  yield put(
    WSCommand(
      "/v1/lifx/command",
      { command: "animate/start", args: original.payload },
      { original }
    )
  );
}

function* removeAnimationSaga(original) {
  yield put(
    WSCommand(
      "/v1/lifx/command",
      { command: "animate/remove", args: original.payload },
      { original }
    )
  );
}

function* displayDiceSaga(original) {
  var { payload } = original;
  var { serial, onFinish } = payload;
  var args = { matcher: { serial } };

  var onerror = ({ error, error_code }) => {
    var errormsg = `${error_code}: ${JSON.stringify(error)}`;
    onFinish(errormsg, []);
  };

  var onsuccess = ({ data }) => {
    var { results, errors } = data;
    var errormsg = undefined;
    if (errors) {
      errormsg = JSON.stringify(errors);
    }
    onFinish(errormsg, results.tiles);
  };

  yield put(
    WSCommand(
      "/v1/lifx/command",
      { command: "tiles/dice", args: args },
      { onerror, onsuccess, original }
    )
  );
}

export function* animationsSaga() {
  yield takeLatest(AnimationsState.EnsureStatusStream, ensureStatusSaga);
  yield takeLatest(AnimationsState.LostStatusStream, lostStatusStreamSaga);
  yield takeLatest(AnimationsState.RemoveAnimation, removeAnimationSaga);
  yield takeLatest(AnimationsState.StartAnimation, startAnimationSaga);
  yield takeLatest(AnimationsState.PauseAnimation, pauseAnimationSaga);
  yield takeLatest(AnimationsState.ResumeAnimation, resumeAnimationSaga);
}

export function* tilesSaga() {
  yield takeLatest(DisplayDice, displayDiceSaga);
}

export const fortests = {
  ensureStatusSaga,
  lostStatusStreamSaga
};

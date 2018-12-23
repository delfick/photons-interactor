import { createAction, createReducer } from "redux-act";

class ControlStateKls {
  Toggle = createAction("Toggle control pane");
  Close = createAction("Close control pane");

  reducer() {
    return createReducer(
      {
        [this.Toggle]: (state, payload) => {
          return { ...state, open: !state.open };
        },
        [this.Close]: (state, payload) => {
          return { ...state, open: false };
        }
      },
      { open: false }
    );
  }
}

export const ControlState = new ControlStateKls();

import { AnimationsState, animationsSaga, tilesSaga } from "./tiles/state.js";
import { SelectionState, selectionSaga } from "./selection/state.js";
import { DevicesState, deviceSaga } from "./device/state.js";
import { ControlState } from "./control/state.js";

import { devToolsEnhancer } from "redux-devtools-extension";
import { applyMiddleware, createStore } from "redux";
import createSagaMiddleware from "redux-saga";
import { combineReducers } from "redux";

export const makeReducer = extra => {
  return combineReducers({
    ...extra,
    control: ControlState.reducer(),
    devices: DevicesState.reducer(),
    selection: SelectionState.reducer(),
    animations: AnimationsState.reducer()
  });
};

export const makeSagaMiddleware = () => {
  return createSagaMiddleware();
};

export const makeStore = (reducer, sagaMiddleware) => {
  const creator = applyMiddleware(sagaMiddleware)(createStore);
  return creator(reducer, devToolsEnhancer());
};

export const runSagaMiddleware = sagaMiddleware => {
  sagaMiddleware.run(deviceSaga);
  sagaMiddleware.run(selectionSaga);
  sagaMiddleware.run(animationsSaga);
  sagaMiddleware.run(tilesSaga);
};

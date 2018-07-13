import { DevicesState, deviceSaga } from "./devices.js";

import { devToolsEnhancer } from "redux-devtools-extension";
import { applyMiddleware, createStore } from "redux";
import createSagaMiddleware from "redux-saga";
import { combineReducers } from "redux";

export const makeReducer = extra => {
  return combineReducers({ ...extra, devices: DevicesState.reducer() });
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
};

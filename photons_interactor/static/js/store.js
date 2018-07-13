import { DevicesState, deviceSaga } from "./devices.js";

import { devToolsEnhancer } from "redux-devtools-extension";
import { applyMiddleware, createStore } from "redux";
import createSagaMiddleware from "redux-saga";
import { combineReducers } from "redux";

const reducer = combineReducers({ devices: DevicesState.reducer() });

const sagaMiddleware = createSagaMiddleware();
const creator = applyMiddleware(sagaMiddleware)(createStore);
const store = creator(reducer, devToolsEnhancer());

sagaMiddleware.run(deviceSaga);

export { store, sagaMiddleware };

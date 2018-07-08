import { applyMiddleware, createStore } from "redux";
import createSagaMiddleware from "redux-saga";
import { combineReducers } from "redux";
import { devToolsEnhancer } from "redux-devtools-extension";

import { DevicesState, deviceSaga } from "./devices.js";

const reducer = combineReducers({ devices: DevicesState.reducer() });

const sagaMiddleware = createSagaMiddleware();
const creator = applyMiddleware(sagaMiddleware)(createStore);
const store = creator(reducer, devToolsEnhancer());

export { store, sagaMiddleware };

sagaMiddleware.run(deviceSaga);

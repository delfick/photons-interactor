// Do polyfills, must happen first
import "babel-core/register";
import "babel-polyfill";

import { routerFork, Routes } from "./router.js";
import { listen } from "./wsclient.js";
import {
  makeReducer,
  makeSagaMiddleware,
  makeStore,
  runSagaMiddleware
} from "./store.js";

import { fork } from "redux-saga/effects";
import { Provider } from "react-redux";
import ReactDOM from "react-dom";
import React from "react";
import "typeface-roboto";

const reducer = makeReducer();
const sagaMiddleware = makeSagaMiddleware();
const store = makeStore(reducer, sagaMiddleware);
runSagaMiddleware(sagaMiddleware);

window.ReactDOM = ReactDOM;
window.Page = (
  <Provider store={store}>
    <Routes />
  </Provider>
);

var scheme = "ws";
if (window.location.protocol.startsWith("https")) {
  scheme = "wss";
}
var url =
  scheme +
  "://" +
  window.location.hostname +
  ":" +
  String(window.location.port) +
  "/v1/ws";

function* mainSaga() {
  yield fork(listen, url);
  yield routerFork;
}

sagaMiddleware.run(mainSaga);

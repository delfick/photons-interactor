// Get csss
import "../css/app.scss";

// Do polyfills, must happen first
import "@babel/register";
import "@babel/polyfill";

import { history, routerSaga } from "./history.js";
import { routerFork, Routes } from "./router.js";
import { listen } from "./wsclient.js";
import {
  makeReducer,
  makeSagaMiddleware,
  makeStore,
  runSagaMiddleware
} from "./store.js";

import { fork, call } from "redux-saga/effects";
import { Provider } from "react-redux";
import ReactDOM from "react-dom";
import React from "react";
import "typeface-roboto";

window.__MUI_USE_NEXT_TYPOGRAPHY_VARIANTS__ = true;

const reducer = makeReducer();
const sagaMiddleware = makeSagaMiddleware();
const store = makeStore(reducer, sagaMiddleware);
runSagaMiddleware(sagaMiddleware);

window.ReactDOM = ReactDOM;
window.Page = (
  <Provider store={store}>
    <Routes history={history} />
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
  yield routerFork(history);
  yield fork(routerSaga);
}

sagaMiddleware.run(mainSaga);

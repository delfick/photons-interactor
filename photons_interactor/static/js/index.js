import { store, sagaMiddleware } from "./store.js";
import { routerFork, Routes } from "./router.js";
import { listen } from "./wsclient.js";

import { fork } from "redux-saga/effects";
import { Provider } from "react-redux";
import ReactDOM from "react-dom";
import React from "react";
import "typeface-roboto";

// Do polyfills
import "babel-core/register";
import "babel-polyfill";

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

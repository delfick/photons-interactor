import React from "react";
import ReactDOM from "react-dom";

import { fork } from "redux-saga/effects";

import "babel-core/register";
import "babel-polyfill";

import "typeface-roboto";

import { routerFork, Routes } from "./router.js";

import { listen } from "./wsclient.js";

import { store, sagaMiddleware } from "./store.js";

import { Provider } from "react-redux";

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

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

function* mainSaga() {
  yield fork(listen);
  yield routerFork;
}

sagaMiddleware.run(mainSaga);

import { DevicesState } from "./devices.js";
import { history } from "./history.js";
import Dashboard from "./dashboard.js";
import Page from "./page.js";

import { Router, Route, Switch } from "react-router";
import { fork, put } from "redux-saga/effects";
import { router } from "redux-saga-router";

const routes = {
  "/": function* indexSaga() {
    yield put(DevicesState.GetSerials());
    yield put(DevicesState.GetDetails());
  }
};

export const routerFork = fork(router, history, routes);

export const Routes = () =>
  <Router history={history}>
    <Page>
      <Switch>
        <Route exact path="/" component={Dashboard} />
      </Switch>
    </Page>
  </Router>;

import { DevicesState } from "./device/state.js";
import Dashboard from "./dashboard.js";
import Page from "./page.js";

import { Router, Route, Switch } from "react-router";
import { fork, put } from "redux-saga/effects";
import { router } from "redux-saga-router";

export const routes = {
  "/": function* indexSaga() {
    yield put(DevicesState.GetSerials());
    yield put(DevicesState.GetDetails());
  }
};

export const routerFork = history => fork(router, history, routes);

export const Routes = ({ history }) =>
  <Router history={history}>
    <Page>
      <Switch>
        <Route exact path="/" component={Dashboard} />
      </Switch>
    </Page>
  </Router>;

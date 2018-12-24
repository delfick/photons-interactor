import { DevicesState } from "./device/state.js";
import { TilesPage } from "./tiles/page.js";
import Dashboard from "./dashboard.js";
import Page from "./page.js";

import { Router, Route, Switch } from "react-router";
import { fork, put } from "redux-saga/effects";
import { router } from "redux-saga-router";

export const routes = {
  "/": function* indexSaga() {
    yield put(DevicesState.GetSerials());
  },
  "/tiles": function* indexSaga() {
    yield put(DevicesState.Refresh());
  }
};

export const routerFork = history => fork(router, history, routes);

export const Routes = ({ history }) => (
  <Router history={history}>
    <Page>
      <Switch>
        <Route exact path="/" component={Dashboard} />
        <Route exact path="/tiles" component={TilesPage} />
      </Switch>
    </Page>
  </Router>
);

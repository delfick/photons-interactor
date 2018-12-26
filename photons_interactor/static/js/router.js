import { AnimationsState } from "./tiles/state.js";
import { DevicesState } from "./device/state.js";
import { TilesPage } from "./tiles/page.js";
import Dashboard from "./dashboard.js";
import Page from "./page.js";

import { Router, Route, Switch } from "react-router";
import { fork, put } from "redux-saga/effects";
import { router } from "redux-saga-router";
import { delay } from "redux-saga";

export const routes = {
  "/": function* indexSaga() {
    yield put(DevicesState.GetSerials());
  },
  "/tiles": function* indexSaga() {
    // Make sure we get animation status info
    yield put(AnimationsState.EnsureStatusStream());

    // Hack so that the WSCommand from Refresh gets seen
    yield delay(1);

    // Make sure we know the devices
    // Don't force a refresh and let user do that themselves if they want
    yield put(DevicesState.GetDetails());
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

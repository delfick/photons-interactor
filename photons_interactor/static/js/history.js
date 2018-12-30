import { ChangePath } from "./router.js";

import createBrowserHistory from "history/createBrowserHistory";
import { createLink } from "redux-saga-router/react";
import { takeLatest } from "redux-saga/effects";

export const history = createBrowserHistory();
export const Link = createLink(history);

function* changeHistorySaga({ payload }) {
  history.push(payload.path);
}

export function* routerSaga() {
  yield takeLatest(ChangePath, changeHistorySaga);
}

import createBrowserHistory from "history/createBrowserHistory";
import { createLink } from "redux-saga-router/react";

export const history = createBrowserHistory();
export const Link = createLink(history);

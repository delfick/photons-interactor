import React from "react";
import ReactDOM from "react-dom";
import Button from "@material-ui/core/Button";

window.ReactDOM = ReactDOM;

const App = () =>
  <Button variant="contained" color="primary">
    Hello World
  </Button>;

window.App = <App />;

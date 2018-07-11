require("babel-register")({
  presets: ["env", "react"],
  plugins: [
    "transform-object-rest-spread",
    "syntax-export-extensions",
    "transform-decorators-legacy",
    "transform-function-bind",
    "transform-class-properties",
    "transform-es2015-template-literals"
  ],
  babelrc: false
});
require("babel-core/register");
require("babel-polyfill");

var WebSocket = require("ws");

global.navigator = { userAgent: "node.js" };
global.WebSocket = WebSocket;

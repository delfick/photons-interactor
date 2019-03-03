require("@babel/register")({
  presets: ["@babel/preset-env", "@babel/preset-react"],
  plugins: [
    ["@babel/plugin-proposal-decorators", { legacy: true }],
    "@babel/transform-runtime",
    "@babel/plugin-proposal-class-properties"
  ],
  babelrc: false
});
require("@babel/polyfill");

var WebSocket = require("ws");

global.navigator = { userAgent: "node.js" };
global.WebSocket = WebSocket;

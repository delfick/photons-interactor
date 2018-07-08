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
global.navigator = { userAgent: "node.js" };

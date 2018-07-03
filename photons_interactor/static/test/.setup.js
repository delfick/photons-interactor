require('babel-register')({
  presets : [ "env", "react" ],
  plugins : [
    "transform-object-rest-spread", "syntax-export-extensions",
    "transform-decorators-legacy", "transform-function-bind",
    "transform-class-properties"
  ],
  babelrc : false
});
global.navigator = {userAgent : 'node.js'};

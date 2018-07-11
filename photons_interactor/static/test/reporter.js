var mocha = require("mocha");
module.exports = Reporter;

var originfo = console.info;
var origerror = console.error;

function Reporter(runner) {
  mocha.reporters.Progress.call(this, runner);
  var passes = 0;
  var failures = 0;

  var logs = [];

  runner.on("start", function() {
    console.info = (...args) => logs.push({ info: args });
    console.error = (...args) => logs.push({ error: args });
  });

  runner.on("end", function() {
    console.info = originfo;
    console.error = origerror;
  });

  runner.on("pass", function(test) {
    logs = [];
  });

  runner.on("fail", function(test, err) {
    logs.map(args => {
      if (args.info) {
        originfo.apply(console, args.info);
      } else if (args.error) {
        origerror.apply(console, args.error);
      }
    });
    logs = [];
  });
}

mocha.utils.inherits(Reporter, mocha.reporters.Progress);

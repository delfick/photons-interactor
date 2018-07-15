import { makeSagaMiddleware, makeStore } from "../js/store.js";

import http from "http";
import path from "path";

export const makeTestStore = reducer => {
  const sagaMiddleware = makeSagaMiddleware();
  const store = makeStore(reducer, sagaMiddleware);
  return { store, sagaMiddleware };
};

export const freePort = () => {
  return new Promise(resolve => {
    var server = http.createServer();
    server.listen(0, "127.0.0.1");
    server.on("listening", function() {
      var port = server.address().port;
      server.close();
      resolve(port);
    });
  });
};

export const waitFor = async (promise, options) => {
  var clear;
  var { reason, timeout } = options || {};
  var msg = lineInfo("waitFor", reason);
  timeout = timeout || 1000;
  timeout = new Promise(function(resolve, reject) {
    clear = setTimeout(function() {
      reject(new Error(`Timedout waiting for a promise: ${msg}`));
    }, timeout);
  });
  try {
    return await Promise.race([promise, timeout]);
  } finally {
    clearTimeout(clear);
  }
};

export const lineInfo = (after, prefix = "") => {
  // Copied with modifications from https://github.com/winstonjs/winston/issues/200#issuecomment-44414591
  var stack = new Error().stack;
  var file, line;

  var record = false;
  var lines = stack.split("\n");
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];
    if (line.includes(after)) {
      if (i + 1 < lines.length) {
        var s = lines[i + 1].split(":");
        file = s[0];
        line = s[1];
        break;
      }
    }
  }

  var [func, file] = file.split(" (");
  if (!file) {
    var [func, file] = ["??", func];
  }
  var [func, file] = [func.split(" ").pop(), path.basename(file)];
  var [junk, func] = func.split(".");
  if (!func) {
    func = junk;
  }
  if (func == "??" || func == "<anonymous>") {
    func = "(";
  } else {
    func = `(<${func}`;
  }
  return `${prefix}${func} ${file}:${line})`;
};

import { createAction, createReducer } from "redux-act";
import assert from "assert";
import { listen } from "../js/wsclient.js";
import WebSocket from "ws";
import { END } from "redux-saga";

import { freePort, waitFor, makeTestStore, lineInfo } from "./helpers.js";
import { WSCommand } from "../js/wsclient.js";

describe("WSClient", function() {
  var deferred = () => {
    var resolve;
    var reject;
    var resolved = false;
    var promise = new Promise((res, rej) => {
      resolve = res;
      reject = rej;
    });
    promise.resolve = d => {
      assert(!resolved);
      resolved = true;
      resolve(d);
    };
    promise.reject = e => {
      assert(!resolved);
      resolved = true;
      reject(e);
    };
    promise.getresolved = () => resolved;
    return promise;
  };

  var GetData = createAction("Get data", () => ({ promise: deferred() }));

  var GotData = createAction("Got data");
  var GotProgress = createAction("Got progress");
  var GotError = createAction("Got error");

  var reducer = function() {
    return createReducer(
      {
        [GotData]: (state, { data, original }) => {
          original.payload.promise.resolve({ data });
          return { ...state, datas: [...state.datas, data] };
        },
        [GotError]: (state, { error, original }) => {
          original.payload.promise.resolve({ error });
          return { ...state, errors: [...state.errors, error] };
        },
        [GotProgress]: (state, { progress, original }) => {
          original.payload.promise.resolve({ progress });
          return { ...state, progresses: [...state.progresses, progress] };
        }
      },
      { datas: [], errors: [], progresses: [] }
    );
  };

  describe("when there is no websocket server", () => {
    var store;
    var wstask;
    var info;
    var port;
    var url;

    before(async () => {
      port = await freePort();
      url = `ws://127.0.0.1:${port}`;
      info = makeTestStore(reducer());
      store = info.store;
      wstask = info.sagaMiddleware.run(listen, url);
    });

    after(async () => {
      if (wstask) {
        wstask.cancel();
        await wstask.done;
      }
    });

    it("fails the command if we can't connect to the server", async () => {
      var original = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { one: "two" },
        { original, onerror: GotError, onsuccess: GotData, timeout: 50 }
      );
      store.dispatch(wscommand);
      var res = await waitFor(original.payload.promise);
      assert.deepEqual(res, {
        error: {
          error: "Timedout waiting for a reply to the message",
          error_code: "Timedout"
        }
      });
    });
  });

  describe("With a running websocket server", () => {
    var actions = [];
    var wsServer;
    var store;
    var wstask;
    var info;
    var port;
    var url;

    var assertActions = (...args) => {
      assert.deepEqual(actions.splice(0, args.length), args);
    };

    before(async () => {
      port = await freePort();
      wsServer = new WebSocket.Server({ port });
      wsServer.on("connection", socket => {
        var send = (message_id, d) =>
          socket.send(JSON.stringify({ ...d, message_id }));

        actions.push("open");

        socket.on("close", () => {
          actions.push("close");
        });

        socket.on("message", data => {
          data = JSON.parse(data);
          assert.equal(data.path, "/v1/test");

          var message_id = data.message_id;
          data = data.body;
          actions.push("message");

          if (data.stop) {
            send(message_id, { closing: true });
            socket.close();
            return;
          }
          if (data.error) {
            send(message_id, { error: data.error, status: 400 });
            return;
          }
          if (data.multiple) {
            data.multiple.map(d => {
              send(message_id, { reply: d });
            });
            return;
          }

          send(message_id, { reply: data });
        });
      });

      url = `ws://127.0.0.1:${port}`;
      info = makeTestStore(reducer());
      store = info.store;
      wstask = info.sagaMiddleware.run(listen, url, 100);
    });

    after(async () => {
      if (wstask) {
        wstask.cancel();
        await wstask.done;
      }
      if (wsServer) {
        wsServer.close(1000, "test ended");
      }
    });

    it("uses onsuccess function to make a reply", async () => {
      var original = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { one: "two" },
        { original, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand);
      var res = await waitFor(original.payload.promise);
      assert.deepEqual(res, { data: { one: "two" } });
      assertActions("open", "message");
    });

    it("reopens on close", async () => {
      var original = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { stop: true },
        { original, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand);
      var res = await waitFor(original.payload.promise);
      assertActions("message", "close");

      var original = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { three: "four" },
        { original, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand);
      var res = await waitFor(original.payload.promise);
      assert.deepEqual(res, { data: { three: "four" } });
      assertActions("open", "message");
    });
  });
});

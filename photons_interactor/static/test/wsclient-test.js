import { createAction, createReducer } from "redux-act";
import { assert } from "chai";
import { listen } from "../js/wsclient.js";
import WebSocket from "ws";
import { END } from "redux-saga";
import { put } from "redux-saga/effects";

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
          original.payload.progress.push(progress);
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

    it("sagas can put inside a finally when a task is cancelled", async () => {
      // This test is because we do a put inside a finally block in processWsReceive
      // And I want to make sure that behaviour works as expected when the saga is cancelled

      var original = GetData();

      var saga = function*() {
        try {
          yield new Promise(() => {});
        } finally {
          yield put(GotData({ data: "PUT", original }));
        }
      };

      var task = info.sagaMiddleware.run(saga);
      await new Promise(resolve => setTimeout(resolve, 10));
      assert(!original.payload.promise.getresolved());

      task.cancel();
      var res = await waitFor(original.payload.promise);
      assert.deepEqual(res, { data: "PUT" });
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
      var sleeps = [];

      wsServer.on("connection", socket => {
        var send = (message_id, d) => {
          if (socket.readyState === 1) {
            socket.send(JSON.stringify({ ...d, message_id }));
          }
        };

        actions.push("open");

        socket.on("close", () => {
          sleeps.map(s => clearTimeout(s));
          actions.push("close");
        });

        socket.on("message", data => {
          data = JSON.parse(data);
          assert.equal(data.path, "/v1/test");

          var message_id = data.message_id;
          data = data.body;
          actions.push("message");

          if (data.sleep) {
            sleeps.push(
              setTimeout(() => {
                send(message_id, { reply: { slept: data.sleep } });
              }, data.sleep)
            );
            return;
          }

          if (data.stop) {
            send(message_id, { reply: { closing: true } });
            socket.close();
            return;
          }
          if (data.error) {
            send(message_id, { error: data.error, status: 400 });
            return;
          }
          if (data.multiple) {
            data.multiple.map(d => {
              actions.push("multi");
              send(message_id, d);
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

    it("a message can timeout", async () => {
      var original = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { sleep: 1000 },
        { original, onerror: GotError, onsuccess: GotData, timeout: 100 }
      );
      store.dispatch(wscommand);
      var res = await waitFor(original.payload.promise);
      assert.deepEqual(res, {
        error: {
          error: "Timedout waiting for a reply to the message",
          error_code: "Timedout"
        }
      });
      assertActions("message");
    });

    it("knows of progress", async () => {
      var original = GetData();
      original.payload.progress = [];

      var wscommand = WSCommand(
        "/v1/test",
        {
          multiple: [
            { progress: "one" },
            { progress: "two" },
            { reply: "three" }
          ]
        },
        {
          original,
          onerror: GotError,
          onsuccess: GotData,
          onprogress: GotProgress
        }
      );
      store.dispatch(wscommand);
      var res = await waitFor(original.payload.promise);
      assert.deepEqual(res, { data: "three" });
      assert.deepEqual(original.payload.progress, ["one", "two"]);
      assertActions("message", "multi", "multi", "multi");
    });

    it("can deal with not having onprogress and getting progress messages", async () => {
      var original = GetData();
      original.payload.progress = [];

      var wscommand = WSCommand(
        "/v1/test",
        {
          multiple: [
            { progress: "one" },
            { progress: "two" },
            { reply: "three" }
          ]
        },
        {
          original,
          onerror: GotError,
          onsuccess: GotData
        }
      );
      store.dispatch(wscommand);
      var res = await waitFor(original.payload.promise);
      assert.deepEqual(res, { data: "three" });
      assert.deepEqual(original.payload.progress, []);
      assertActions("message", "multi", "multi", "multi");
    });

    it("ignores multiple replies", async () => {
      var original = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { multiple: [{ reply: "one" }, { reply: "two" }] },
        { original, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand);
      var res = await waitFor(original.payload.promise);
      assert.deepEqual(res, { data: "one" });
      assertActions("message", "multi", "multi");
    });

    it("errors messages we're still waiting for when the server closes", async () => {
      var original1 = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { sleep: 50 },
        { original: original1, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand);

      var original2 = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { stop: true },
        { original: original2, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand);

      await waitFor(original2.payload.promise);
      var res = await waitFor(original1.payload.promise);
      assert.deepEqual(res, {
        error: {
          error: "Lost connection to the server",
          error_code: "LostConnection"
        }
      });
      assertActions("message", "message");

      // The lost connection error above means we will now be waiting for the next socket
      // So waiting for another message is same as waiting for socket to be open again
      var original3 = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { five: "six" },
        { original: original3, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand);
      await waitFor(original3.payload.promise);
      assertActions("close", "open", "message");
    });

    it("assigns out of order replies correctly", async () => {
      var original1 = GetData();
      var wscommand1 = WSCommand(
        "/v1/test",
        { sleep: 100 },
        { original: original1, onerror: GotError, onsuccess: GotData }
      );

      var original2 = GetData();
      var wscommand2 = WSCommand(
        "/v1/test",
        { sleep: 20 },
        { original: original2, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand1);
      store.dispatch(wscommand2);

      var p1 = new Promise(resolve => {
        waitFor(original1.payload.promise).then(res => {
          assert.deepEqual(res, { data: { slept: 100 } });
          resolve(Date.now());
        });
      });

      var p2 = new Promise(resolve => {
        waitFor(original2.payload.promise).then(res => {
          assert.deepEqual(res, { data: { slept: 20 } });
          resolve(Date.now());
        });
      });

      var d1 = await waitFor(p1);
      var d2 = await waitFor(p2);
      assert.isAbove(d1 - d2, 0);
      assert.isBelow(d1 - d2, 90);

      assertActions("message", "message");
    });

    it("reopens on close", async () => {
      var original1 = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { sleep: 50 },
        { original: original1, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand);

      var original2 = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { stop: true },
        { original: original2, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand);

      // Wait for the socket to close
      var res = await waitFor(original2.payload.promise);
      assert.deepEqual(res, { data: { closing: true } });

      // Waiting for this to have failed means the next message goes to a new socket
      await waitFor(original1.payload.promise);

      var original = GetData();
      var wscommand = WSCommand(
        "/v1/test",
        { three: "four" },
        { original, onerror: GotError, onsuccess: GotData }
      );
      store.dispatch(wscommand);
      var res = await waitFor(original.payload.promise);
      assert.deepEqual(res, { data: { three: "four" } });

      assertActions("message", "message", "close", "open", "message");
    });
  });
});
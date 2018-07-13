import { eventChannel, channel, END, delay } from "redux-saga";
import { createAction } from "redux-act";
import { call, spawn, cancel, fork, put, take, race } from "redux-saga/effects";

import uuidv4 from "uuid/v4";

export const WSCommand = createAction(
  "Command to the websocket server",
  (path, body, { onsuccess, onerror, onprogress, timeout, original }) => ({
    path,
    body,
    onsuccess,
    onerror,
    onprogress,
    timeout,
    original
  })
);

function* maybeTimeoutMessage(action) {
  yield call(delay, action.timeout || 5000);
  var response = action.onerror({
    error: "Timedout waiting for a reply to the message",
    error_code: "Timedout"
  });
  if (response) {
    yield put(response);
  }
}

function* sendToSocket(socket, sendch) {
  while (true) {
    var action = yield take(sendch);
    if (socket.readyState === 1) {
      socket.send(JSON.stringify(action.data));
    } else {
      var response = action.onerror({
        error: "Connection to the server wasn't active",
        error_code: "InactiveConnection"
      });
      if (response) {
        yield put(response);
      }
    }
  }
}

function* tickMessages(socket) {
  while (true) {
    yield call(delay, 15000);
    if (socket.readyState === 1) {
      socket.send(JSON.stringify({ path: "__tick__" }));
    }
  }
}

function* startWS(url, count, sendch, receivech) {
  var socket = new WebSocket(url);

  var onerrors = [];
  var oncloses = [];

  var ws = new Promise((resolve, reject) => {
    socket.onopen = () => {
      resolve(socket);
    };

    socket.onmessage = event => receivech.put(event);

    socket.onerror = evt => {
      console.error("Websocket got error", evt);
      reject(evt);
    };

    socket.onclose = evt => {
      console.error("Websocket closed", evt);
      reject(evt);
      oncloses.map(cb => {
        try {
          cb(evt);
        } catch (e) {
          console.error(e);
        }
      });
    };
  });

  var start = Date.now();

  try {
    var { timeout, w } = yield race({ timeout: call(delay, 2000), w: ws });
  } catch (e) {
    console.error("Failed to start websocket connection", e);
    var diff = Date.now() - start;
    if (diff < 1000) {
      yield call(delay, 1000 - diff);
    }
    return;
  }

  if (timeout) {
    console.error("timed out waiting for websocket");
    socket.close();
    return false;
  }

  var waiter = yield call(channel);
  var ticker = yield fork(tickMessages, w);
  var sender = yield fork(sendToSocket, w, sendch);

  oncloses.push(() => {
    waiter.put(END);
  });

  try {
    yield take(waiter);
  } finally {
    waiter.close();
    yield cancel(ticker);
    yield cancel(sender);
  }
}

function* processWsSend(commandch, sendch, actions) {
  var normalise = (
    messageId,
    { path, body, onerror, onsuccess, onprogress, original, timeout }
  ) => {
    var done = false;

    var data = { path, body, message_id: messageId };
    var doerror = error => {
      if (done) {
        return;
      }

      done = true;
      if (onerror) {
        return onerror({ messageId, error, original });
      }
    };

    var dosuccess = (data, msgid) => {
      if (done) {
        return;
      }

      done = true;
      if (onsuccess) {
        return onsuccess({ messageId, data, original });
      }
    };

    var doprogress = progress => {
      if (onprogress) {
        return onprogress({ messageId, progress, original });
      }
    };

    return {
      data,
      messageId,
      timeout: timeout,
      onsuccess: dosuccess,
      onerror: doerror,
      onprogress: doprogress
    };
  };

  while (true) {
    var { payload } = yield take(commandch);
    var messageId = uuidv4();
    var normalised = normalise(messageId, payload);
    actions[messageId] = normalised;
    normalised.timeouter = yield spawn(maybeTimeoutMessage, normalised);
    yield put(sendch, normalised);
  }
}

function* processWsReceive(receivech, actions) {
  var makeResponse = (action, data) => {
    if (data.progress) {
      return action.onprogress(data.progress);
    }

    if (data.reply) {
      if (data.reply.error) {
        return action.onerror(data.reply);
      } else {
        return action.onsuccess(data.reply, data.message_id);
      }
    }

    if (data.error) {
      return action.onerror(data.error);
    }
  };

  while (true) {
    var { data } = yield take(receivech);
    try {
      data = JSON.parse(data);
    } catch (e) {
      console.error("failed to parse json from the server", e);
      continue;
    }

    if (!data.message_id) {
      console.error("Got a message from the server without a message id", data);
      continue;
    }

    if (data.message_id == "__tick__") {
      continue;
    }

    var action = actions[data.message_id];

    if (!action) {
      console.error(
        "Got a message from the server with unknown message id",
        data.message_id,
        data
      );
      continue;
    }

    if (action.timeouter) {
      yield cancel(action.timeouter);
    }

    let response = undefined;
    try {
      response = makeResponse(action, data);
    } finally {
      // Really make sure we put our response
      // This is because once the response is made,
      // no other response can be made
      if (response) {
        yield put(response);
      }
    }

    // Finished with this message
    delete actions[data.message_id];
  }
}

export function* getWSCommands(commandch) {
  while (true) {
    var nxt = yield take(WSCommand);
    yield put(commandch, nxt);
  }
}

export function* listen(url, delayMS) {
  var count = 0;
  var messages = {};
  var sendch = yield call(channel);
  var receivech = yield call(channel);
  var commandch = yield call(channel);

  yield fork(getWSCommands, commandch);

  while (true) {
    count += 1;
    var actions = {};
    messages[count] = actions;
    var sendprocess = yield fork(processWsSend, commandch, sendch, actions);
    var receiveprocess = yield fork(processWsReceive, receivech, actions);
    yield call(startWS, url, count, sendch, receivech);
    yield cancel(sendprocess);
    yield cancel(receiveprocess);

    var ids = Object.keys(actions);
    for (var i = 0; i < ids.length; i++) {
      var action = actions[ids[i]];
      if (action.timeouter) {
        yield cancel(action.timeouter);
      }

      var response = action.onerror({
        error: "Lost connection to the server",
        error_code: "LostConnection"
      });
      if (response) {
        yield put(response);
      }
    }

    delete messages[count];
    yield call(delay, delayMS || 5000);
  }
}

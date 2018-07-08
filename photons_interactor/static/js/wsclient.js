import { eventChannel, channel, END, delay } from "redux-saga";
import { createAction } from "redux-act";
import { call, cancel, fork, put, take, race } from "redux-saga/effects";

import uuidv4 from "uuid/v4";

export const WSCommand = createAction(
  "Command to the websocket server",
  (path, body, { onsuccess, onerror, onprogress }) => ({
    path,
    body,
    onsuccess,
    onerror,
    onprogress
  })
);

function* sendToSocket(socket, sendch) {
  while (true) {
    var action = yield take(sendch);
    if (socket.readyState === 1) {
      socket.send(JSON.stringify(action.data));
    } else {
      yield put(sendch, action);
      break;
    }
  }
}

function tickMessages(socket) {
  var send_tick = () => {
    if (socket.readyState === 1) {
      socket.send(JSON.stringify({ path: "__tick__" }));
    }
  };

  var interval = setInterval(send_tick, 15000);

  return eventChannel(emit => {
    return () => {
      clearInterval(interval);
    };
  });
}

function* startWS(count, sendch, receivech) {
  var scheme = "ws";
  if (window.location.protocol.startsWith("https")) {
    scheme = "wss";
  }
  var socket = new WebSocket(
    scheme +
      "://" +
      window.location.hostname +
      ":" +
      String(window.location.port) +
      "/v1/ws"
  );

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
      onerrors.map(cb => {
        try {
          cb(evt);
        } catch (e) {
          console.error(e);
        }
      });
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

  var addonerror = cb => onerrors.push(cb);
  var addonclose = cb => oncloses.push(cb);

  try {
    var { timeout, w } = yield race({ timeout: call(delay, 2000), w: ws });
  } catch (e) {
    console.error("Failed to start websocket connection", e);
    return;
  }

  if (timeout) {
    console.error("timed out waiting for websocket");
    socket.close();
    return false;
  }

  var ticker = yield call(tickMessages, w);
  var sender = yield call(sendToSocket, w, sendch);

  yield take(
    eventChannel(emit => {
      addonclose(() => {
        emit.put(END);
      });
    })
  );

  yield cancel(ticker);
  yield cancel(sender);
}

function* processWsSend(sendch, actions) {
  var normalise = (
    messageId,
    { path, body, onerror, onsuccess, onprogress }
  ) => {
    var done = false;

    var data = { path, body, message_id: messageId };
    var doerror = error => {
      if (done) {
        return;
      }

      done = true;
      if (onerror) {
        return onerror({ messageId, error });
      }
    };

    var dosuccess = data => {
      if (done) {
        return;
      }

      done = true;
      if (onsuccess) {
        return onsuccess({ messageId, data });
      }
    };

    var doprogress = data => {
      if (done) {
        return;
      }

      done = true;
      if (onprogress) {
        return onprogress({ messageId, data });
      }
    };

    return {
      data,
      onsuccess: dosuccess,
      onerror: doerror,
      onprogress: doprogress
    };
  };
  while (true) {
    var { payload } = yield take(WSCommand);
    var messageId = uuidv4();
    var normalised = normalise(messageId, payload);
    actions[messageId] = normalised;
    yield put(sendch, normalised);
  }
}

function* processWsReceive(receivech, actions) {
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

    var response;
    if (data.progress) {
      response = action.onprogress(data.progress);
    } else if (data.reply) {
      if (data.reply.error) {
        response = action.onerror(data.reply);
      } else {
        response = action.onsuccess(data.reply);
      }
    } else if (data.error) {
      response = action.onerror(data.error);
    }

    if (response) {
      yield put(response);
    }
  }
}

export function* listen(ch, delayMS) {
  var count = 0;
  var messages = {};
  var sendch = yield call(channel);
  var receivech = yield call(channel);

  while (true) {
    count += 1;
    var actions = {};
    messages[count] = actions;
    var sendprocess = yield fork(processWsSend, sendch, actions);
    var receiveprocess = yield fork(processWsReceive, receivech, actions);
    yield call(startWS, count, sendch, receivech);
    yield cancel(sendprocess);
    yield cancel(receiveprocess);
    Object.keys(actions).map(messageId => {
      var action = actions[messageId];
      action.onerror("Lost connection to the server");
    });
    delete messages[count];
    yield call(delay, delayMS || 5000);
  }
}

.. _commands:

Commands
========

The server also lets you talk to it over http or websockets.

Over http, you make PUT requests like the following::

    $ curl -XPUT http://localhost:6100/v1/lifx/command \
      -HContent-Type:application/json \
      -d '{"command": "help", "args": {"command": "transform"}}'

The reply will always look like:

.. code-block:: plain

    {
      "results": {
        <serial>: <result>,
        <serial>: <result>
      },
      "errors": [<error>, <error>]
    }

Each serial result may have their own ``error`` key.

Over websockets you make a websocket connection to `ws://localhost:6100/v1/ws`
and send messages to it like:

.. code-block::  plain

    {
      path: "/v1/lifx/command",
      body: {
        "command": "discover",
        "args": {"refresh": false}
      },
      "message_id": "unique identifier"
    }

The path is the same as the ``path`` segment of the HTTP commands and the
``body`` is the same as the body you would send to the HTTP server.
The ``message_id`` is a unique identify you give to the request so that you
can match progress and response messages to your request.

The response will either be:

.. code-block:: plain

    {
      "reply": <results>,
      "message_id": <message_id_from_request>
    }

The result to ``reply`` may be a dictionary with ``error`` in it, a dictionary
with ``progress`` in it, or the result.

Discovering commands
--------------------

You can find available commands by running::

    $ curl -XPUT http://localhost:6100/v1/lifx/command \
      -HContent-Type:application/json \
      -d '{"command": "help"}'

And then for each command you can find more information by saying::

    $ curl -XPUT http://localhost:6100/v1/lifx/command \
      -HContent-Type:application/json \
      -d '{"command": "help", "args": {"command": "transform"}}'

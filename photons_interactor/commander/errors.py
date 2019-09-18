from photons_app.errors import PhotonsAppError


class NoSuchCommand(PhotonsAppError):
    desc = "no such command"


class NoSuchPacket(PhotonsAppError):
    desc = "no such packet"


class NoSuchScene(PhotonsAppError):
    desc = "no such scene"


class InvalidArgs(PhotonsAppError):
    desc = "Invalid arguments"


class NotAWebSocket(PhotonsAppError):
    desc = "Request wasn't a websocket"

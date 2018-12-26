from photons_interactor.request_handlers.command import MessageFromExc
from photons_interactor.commander import default_fields as df
from photons_interactor.commander import helpers as chp
from photons_interactor.commander.store import store

from photons_app.errors import PhotonsAppError, FoundNoDevices
from photons_app import helpers as hp

from photons_tile_paint.animation import Finish
from photons_tile_paint.addon import Animations

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from tornado import websocket
import logging
import asyncio
import time
import uuid

log = logging.getLogger("photons_interactor.commander.commands.animations")

class NoSuchAnimation(PhotonsAppError):
    desc = "No such animation"

class FoundNoTiles(PhotonsAppError):
    desc = "No tiles could be found"

class AllSerialsAlreadyAnimating(PhotonsAppError):
    desc = "Can't start animation on already animating devices"

class NotAWebSocket(PhotonsAppError):
    desc = "Request wasn't a websocket"

class valid_animation_name(sb.Spec):
    def normalise_filled(self, meta, val):
        animations = meta.everything["animations"]
        return sb.string_choice_spec(list(animations.animators)).normalise(meta, val)

class AnimationsStore:
    _merged_options_formattable = True

    def __init__(self):
        self.animations = {}
        self.animators = dict(Animations.animators())
        self.listeners = {}

    def add_listener(self):
        u = str(uuid.uuid4())
        self.listeners[u] = hp.ResettableFuture()
        self.listeners[u].cancel()
        return u, self.listeners[u]

    def remove_listener(self, u):
        if u in self.listeners:
            del self.listeners[u]

    def activate_listeners(self):
        for fut in self.listeners.values():
            fut.cancel()

    def available(self):
        return list(self.animators)

    def start(self, animation, target, serials, reference, afr, options, stop_conflicting=False):
        if animation not in self.animators:
            raise NoSuchAnimation(wanted=animation, available=list(self.animators))

        conflicting = set()
        for aid, info in self.animations.items():
            if not info["task_future"].done():
                for s in info["serials"]:
                    if s in serials:
                        if stop_conflicting:
                            self.stop(aid)
                        else:
                            conflicting.add(s)

        remaining = set(serials) - conflicting
        if not remaining:
            raise AllSerialsAlreadyAnimating(want=serials, conflicting=list(conflicting))
        serials = list(remaining)

        animation_id = str(uuid.uuid4())

        pauser = asyncio.Condition()
        final_future = asyncio.Future()
        info = {
              "pauser": pauser
            , "paused": False
            , "final_future": final_future
            , "started": time.time()
            , "serials": serials
            , "name": self.animators[animation].name
            }

        async def coro():
            try:
                await self.animators[animation].animate(target, afr, final_future, reference, options
                    , pauser=info["pauser"]
                    )
            except Finish:
                pass
        task_future = asyncio.ensure_future(hp.async_as_background(coro()))

        info["task_future"] = task_future

        async def remove_after_a_minute():
            await asyncio.sleep(60)
            self.remove(animation_id)

        def activate(*args):
            self.activate_listeners()
            if "stopped" not in info:
                info["stopped"] = time.time()
            hp.async_as_background(remove_after_a_minute())
        info["task_future"].add_done_callback(activate)

        self.animations[animation_id] = info
        self.activate_listeners()
        return animation_id

    async def pause(self, animation_id):
        if animation_id in self.animations:
            info = self.animations[animation_id]
            if info["final_future"].done():
                return

            if not info["paused"]:
                self.animations[animation_id]["paused"] = True
                await self.animations[animation_id]["pauser"].acquire()
                self.activate_listeners()

    def resume(self, animation_id):
        if animation_id in self.animations:
            info = self.animations[animation_id]
            if info["final_future"].done():
                return

            if info["paused"]:
                info["paused"] = False
                info["pauser"].release()
                self.activate_listeners()

    def stop(self, animation_id):
        if animation_id in self.animations:
            self.resume(animation_id)

            info = self.animations[animation_id]
            info["final_future"].cancel()
            if "stopped" not in self.animations[animation_id]:
                info["stopped"] = time.time()

            self.activate_listeners()

    def remove(self, animation_id):
        self.stop(animation_id)
        if animation_id in self.animations:
            del self.animations[animation_id]
        self.activate_listeners()

    def remove_all(self):
        for aid in list(self.animations):
            self.stop(aid)
            del self.animations[aid]
        self.activate_listeners()

    def status(self, animation_id):
        status = {}

        animation_ids = [animation_id]
        if animation_id in (None, sb.NotSpecified):
            animation_ids = list(self.animations)

        for aid in animation_ids:
            if aid in self.animations:
                info = self.animations[aid]
                s = status[aid] = {}
                s["name"] = info["name"]
                s["started"] = info["started"]
                s["serials"] = info["serials"]
                if "stopped" in info:
                    s["took"] = info["stopped"] - info["started"]
                    s["stopped"] = info["stopped"]
                s["paused"] = info["paused"]
                s["running"] = not info["task_future"].done()
                s["cancelled"] = info["final_future"].done()

                if info["task_future"].done() and not info["task_future"].cancelled():
                    exc = info["task_future"].exception()
                    if exc is not None:
                        s["error"] = MessageFromExc()(type(exc), exc, exc.__traceback__)

        num_running = sum(1 for an in self.animations.values() if not an["task_future"].done())

        return {
              "num_animations": len(self.animations)
            , "running_animations": num_running
            , "statuses": status
            }

@store.command(name="animate/available")
class AvailableAnimateCommand(store.Command):
    """
    Return available animations
    """
    animations = store.injected("animations")

    async def execute(self):
        response = []
        for name in sorted(self.animations.animators):
            response.append({"name": name})

        return {"animations": response}

@store.command(name="animate/start")
class StartAnimateCommand(store.Command):
    """
    Start a tile animation
    """
    finder = store.injected("finder")
    target = store.injected("targets.lan")
    animations = store.injected("animations")

    matcher = df.matcher_field
    refresh = df.refresh_field

    animation = dictobj.Field(valid_animation_name, wrapper=sb.required)
    options = dictobj.Field(sb.dictionary_spec)
    stop_conflicting = dictobj.Field(sb.boolean, default=False)

    async def execute(self):
        afr = await self.finder.args_for_run()
        fltr = chp.filter_from_matcher(self.matcher)

        if self.refresh is not None:
            fltr.force_refresh = self.refresh

        found_serials = await self.finder.serials(filtr=fltr)

        fltr = chp.filter_from_matcher({"serial": found_serials, "cap": "chain"})
        try:
            serials = await self.finder.serials(filtr=fltr)
        except FoundNoDevices:
            raise FoundNoTiles(matcher=self.matcher)

        find_fltr = chp.clone_filter(fltr, force_refresh=False)
        reference = self.finder.find(filtr=find_fltr)

        animation_id = self.animations.start(self.animation
            , self.target, serials, reference, afr, self.options
            , stop_conflicting = self.stop_conflicting
            )
        return {"animation_id": animation_id}

@store.command(name="animate/stop")
class StopAnimateCommand(store.Command):
    """
    Stop a tile animation
    """
    animations = store.injected("animations")

    animation_id = dictobj.Field(sb.string_spec, wrapper=sb.required)

    async def execute(self):
        self.animations.stop(self.animation_id)
        return {"success": True}

@store.command(name="animate/pause")
class PauseAnimateCommand(store.Command):
    """
    Pause a tile animation
    """
    animations = store.injected("animations")

    animation_id = dictobj.Field(sb.string_spec, wrapper=sb.required)

    async def execute(self):
        await self.animations.pause(self.animation_id)
        return {"success": True}

@store.command(name="animate/resume")
class ResumeAnimateCommand(store.Command):
    """
    Resume a tile animation
    """
    animations = store.injected("animations")

    animation_id = dictobj.Field(sb.string_spec, wrapper=sb.required)

    async def execute(self):
        self.animations.resume(self.animation_id)
        return {"success": True}

@store.command(name="animate/remove")
class RemoveAnimateCommand(store.Command):
    """
    Stop and remove a tile animation
    """
    animations = store.injected("animations")

    animation_id = dictobj.Field(sb.string_spec, wrapper=sb.required)

    async def execute(self):
        self.animations.remove(self.animation_id)
        return {"success": True}

@store.command(name="animate/remove_all")
class RemoveAllAnimateCommand(store.Command):
    """
    Stop and remove all animations
    """
    animations = store.injected("animations")

    async def execute(self):
        self.animations.remove_all()
        return {"success": True}

@store.command(name="animate/status")
class StatusAnimateCommand(store.Command):
    """
    Return status of an animation
    """
    animations = store.injected("animations")

    animation_id = dictobj.Field(sb.string_spec, wrapper=sb.optional_spec)

    async def execute(self):
        return self.animations.status(self.animation_id)

@store.command(name="animate/status_stream")
class StatusStreamAnimateCommand(store.Command):
    """
    An endless stream of updates to animation status
    """
    animations = store.injected("animations")
    progress_cb = store.injected("progress_cb")
    request_handler = store.injected("request_handler")

    async def execute(self):
        if not isinstance(self.request_handler, websocket.WebSocketHandler):
            raise NotAWebSocket("status stream can only be called from a websocket")

        u, fut = self.animations.add_listener()
        self.progress_cb({"available": self.animations.available()})

        while True:
            await asyncio.wait([self.request_handler.connection_future, fut], return_when=asyncio.FIRST_COMPLETED)

            if self.request_handler.connection_future.done():
                log.info(hp.lc("Connection to status stream went away"))
                self.animations.remove_listener(u)
                break

            self.progress_cb({"status": self.animations.status(sb.NotSpecified)})
            fut.reset()

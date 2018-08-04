from photons_interactor.database.database import Scene, SceneInfo
from photons_interactor.commander.commands.base import Command
from photons_interactor.commander import default_fields as df
from photons_interactor.commander.errors import NoSuchScene
from photons_interactor.commander.decorator import command
from photons_interactor.commander import helpers as chp

from photons_app.errors import FoundNoDevices
from photons_app import helpers as hp

from photons_transform.transformer import Transformer
from photons_device_messages import DeviceMessages
from photons_multizone import MultiZoneMessages
from photons_tile_messages import TileMessages
from photons_colour import ColourMessages

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from collections import defaultdict
import uuid

@command(name="scene_info")
class SceneInfoCommand(Command):
    """
    Retrieve information about scenes in the database
    """
    db_queue = df.db_queue_field

    uuid = dictobj.NullableField(sb.listof(sb.string_spec())
        , help = "Only get information for scene with these uuid"
        )

    only_meta = dictobj.Field(sb.boolean, default=False
        , help = "Only return meta info about the scenes"
        )

    async def execute(self):
        def get(db):
            info = defaultdict(lambda: {"meta": {}, "scene": []})

            fs = []
            ifs = []
            if self.uuid:
                fs.append(Scene.uuid.in_(self.uuid))
                ifs.append(SceneInfo.uuid.in_(self.uuid))

            for sinfo in db.query(SceneInfo).filter(*ifs):
                info[sinfo.uuid]["meta"] = sinfo.as_dict(ignore=["uuid"])

            for scene in db.query(Scene).filter(*fs):
                # Make sure there is an entry if no SceneInfo for this scene
                info[scene.uuid]

                if not self.only_meta:
                    dct = scene.as_dict(ignore=["uuid"])
                    info[scene.uuid]["scene"].append(dct)

            if self.only_meta:
                for _, data in info.items():
                    del data["scene"]

            return dict(info)
        return await self.db_queue.request(get)

@command(name="scene_change")
class SceneChangeCommand(Command):
    """
    Set all the options for a scene
    """
    db_queue = df.db_queue_field

    uuid = dictobj.NullableField(sb.string_spec
        , help = "The uuid of the scene to change, if None we create a new scene"
        )

    label = dictobj.NullableField(sb.string_spec
        , help = "The label to give this scene"
        )

    description = dictobj.NullableField(sb.string_spec
        , help = "The description to give this scene"
        )

    scene = dictobj.NullableField(sb.listof(Scene.DelayedSpec(storing=True))
        , help = "The options for the scene"
        )

    async def execute(self):
        def make(db):
            scene_uuid = self.uuid or str(uuid.uuid4())

            if self.scene is not None:
                for thing in db.queries.get_scenes(uuid=scene_uuid).all():
                    db.delete(thing)

                for part in self.scene:
                    made = db.queries.create_scene(**part(scene_uuid).as_dict())
                    db.add(made)

            info, _ = db.queries.get_or_create_scene_info(uuid=scene_uuid)
            if self.label is not None:
                info.label = self.label
            if self.description is not None:
                info.description = self.description
            db.add(info)

            return scene_uuid
        return await self.db_queue.request(make)

@command(name="scene_delete")
class SceneDeleteCommand(Command):
    """
    Delete a scene
    """
    db_queue = df.db_queue_field

    uuid = dictobj.Field(sb.string_spec, wrapper=sb.required
        , help = "The uuid of the scene to delete"
        )

    async def execute(self):
        def delete(db):
            for thing in db.queries.get_scenes(uuid=self.uuid).all():
                db.delete(thing)

            return {"deleted": True}
        return await self.db_queue.request(delete)

@command(name="scene_apply")
class SceneApplyCommand(Command):
    """
    Apply a scene
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    timeout = df.timeout_field
    db_queue = df.db_queue_field

    uuid = dictobj.Field(sb.string_spec, wrapper=sb.required
        , help = "The uuid of the scene to apply"
        )

    overrides = dictobj.Field(sb.dictionary_spec
        , help = "Overrides to the scene"
        )

    async def execute(self):
        ts = []
        result = chp.ResultBuilder()

        def get(db):
            info = []
            for scene in db.queries.get_scenes(uuid=self.uuid).all():
                info.append(scene.as_object())
            if not info:
                raise NoSuchScene(uuid=self.uuid)
            return info

        for scene in await self.db_queue.request(get):
            fltr = chp.filter_from_matcher(scene.matcher, False)

            if scene.zones:
                multizonefltr = self.clone_fltr_with_cap(fltr, "multizone")
                ts.append(hp.async_as_background(self.apply_zones(multizonefltr, scene, result)))

                notmultizonefltr = self.clone_fltr_with_no_cap(fltr, "multizone")
                ts.append(hp.async_as_background(self.transform(notmultizonefltr, scene, result)))

            elif scene.chain:
                chainfltr = self.clone_fltr_with_cap(fltr, "chain")
                ts.append(hp.async_as_background(self.apply_chain(chainfltr, scene, result)))

                notchainfltr = self.clone_fltr_with_no_cap(fltr, "chain")
                ts.append(hp.async_as_background(self.transform(notchainfltr, scene, result)))

            else:
                ts.append(hp.async_as_background(self.transform(fltr, scene, result)))

        for t in ts:
            try:
                await t
            except Exception as error:
                result.error(error)

        return result

    async def transform(self, fltr, scene, result):
        options = scene.transform_options
        options.update(self.overrides)
        options["duration"] = options["duration"] or 0

        msg = Transformer.using(options)
        script = self.target.script(msg)
        try:
            await chp.run(script, fltr, self.finder, add_replies=False, timeout=self.timeout, result=result)
        except FoundNoDevices:
            pass

    async def apply_zones(self, fltr, scene, result):
        script = self.target.script(list(scene.zone_msgs(self.overrides)))
        try:
            await chp.run(script, fltr, self.finder, add_replies=False, timeout=self.timeout, result=result)
        except FoundNoDevices:
            pass

    async def apply_chain(self, fltr, scene, result):
        script = self.target.script(list(scene.chain_msgs(self.overrides)))
        try:
            await chp.run(script, fltr, self.finder, add_replies=False, timeout=self.timeout, result=result)
        except FoundNoDevices:
            pass

    def clone_fltr_with_no_cap(self, fltr, cap):
        clone = fltr.clone()
        if clone.cap is sb.NotSpecified:
            clone.cap = [f"not_{cap}"]
        else:
            clone.cap.append(cap)
            clone.cap = [c for c in clone.cap if c != cap]
        return clone

    def clone_fltr_with_cap(self, fltr, cap):
        clone = fltr.clone()
        if clone.cap is sb.NotSpecified:
            clone.cap = [cap]
        else:
            clone.cap.append(cap)
            clone.cap = [c for c in clone.cap if c != f"not_{cap}"]
        return clone

@command(name="scene_capture")
class SceneCaptureCommand(Command):
    """
    Capture a scene
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    refresh = df.refresh_field
    db_queue = df.db_queue_field
    commander = df.commander_field

    uuid = dictobj.NullableField(sb.string_spec
        , help = "The uuid of the scene to change, if None we create a new scene"
        )

    label = dictobj.NullableField(sb.string_spec
        , help = "The label to give this scene"
        )

    description = dictobj.NullableField(sb.string_spec
        , help = "The description to give this scene"
        )

    just_return = dictobj.Field(sb.boolean, default=False
        , help = "Just return the scene rather than storing it in the database"
        )

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        details = await self.finder.info_for(filtr=fltr)

        msgs = []
        for serial, info in details.items():
            msgs.append(DeviceMessages.GetPower(target=serial))

            if "multizone" in info["cap"]:
                msgs.append(MultiZoneMessages.GetMultiZoneColorZones(start_index=0, end_index=255, target=serial))
            elif "chain" in info["cap"]:
                msgs.append(TileMessages.GetTileState64(tile_index=0, length=5, x=0, y=0, width=8, target=serial))
            else:
                msgs.append(ColourMessages.GetColor(target=serial))

        state = defaultdict(dict)
        afr = await self.finder.args_for_run()
        async for pkt, _, _ in self.target.script(msgs).run_with(None, afr, multiple_replies=True, first_wait=0.5):
            if pkt | DeviceMessages.StatePower:
                state[pkt.serial]["power"] = pkt.level != 0
            elif pkt | ColourMessages.LightState:
                hsbk = f"kelvin:{pkt.kelvin} saturation:{pkt.saturation} brightness:{pkt.brightness} hue:{pkt.hue}"
                state[pkt.serial]["color"] = hsbk
            elif pkt | MultiZoneMessages.StateMultiZoneStateMultiZones:
                if "zones" not in state[pkt.serial]:
                    state[pkt.serial]["zones"] = []
                for i, zi in enumerate(range(pkt.zone_index, pkt.zone_index + 8)):
                    c = pkt.colors[i]
                    state[pkt.serial]["zones"].append((zi, [c.hue, c.saturation, c.brightness, c.kelvin]))
            elif pkt | TileMessages.StateTileState64:
                if "chain" not in state[pkt.serial]:
                    state[pkt.serial]["chain"] = []
                colors = [[c.hue, c.saturation, c.brightness, c.kelvin] for c in pkt.colors]
                state[pkt.serial]["chain"].append((pkt.tile_index, colors))

        scene = []
        for serial, info in sorted(state.items()):
            if "zones" in info:
                info["zones"] = [hsbk for _, hsbk in sorted(info["zones"])]
            if "chain" in info:
                info["chain"] = [hsbks for _, hsbks in sorted(info["chain"])]

            scene.append({"matcher": {"serial": serial}, **info})

        if self.just_return:
            return scene

        args = {
              "uuid": self.uuid
            , "scene": scene
            , "label": self.label
            , "description": self.description
            }
        return await self.commander.execute({"command": "scene_change", "args": args})
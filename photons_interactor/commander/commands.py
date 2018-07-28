from photons_interactor.commander.errors import NoSuchCommand
from photons_interactor.commander import default_fields as df
from photons_interactor.commander.decorator import command
from photons_interactor.commander import helpers as chp
from photons_interactor.database.database import Scene

from photons_transform.transformer import Transformer

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from collections import defaultdict
from textwrap import dedent
import uuid

class Command(dictobj.Spec):
    async def execute(self):
        raise NotImplementedError("Base command has no execute implementation")

@command(name="help")
class HelpCommand(Command):
    """
    Display the documentation for the specified command
    """
    command = dictobj.Field(sb.string_spec, default="help"
        , help = "The command to show help for"
        )

    @property
    def command_kls(self):
        if self.command not in command.available_commands:
            raise NoSuchCommand(wanted=self.command, available=sorted(command.available_commands))
        return command.available_commands[self.command]["kls"]

    async def execute(self):
        header = f"Command {self.command}"
        kls = self.command_kls
        doc = dedent(getattr(kls, "__help__", kls.__doc__))

        fields = chp.fields_description(kls)
        fields_string = ""
        if fields:
            fields_string = ["", "Arguments\n---------", ""]
            for name, type_info, desc in fields:
                fields_string.append(f"{name}: {type_info}")
                for line in desc.split("\n"):
                    if not line.strip():
                        fields_string.append("")
                    else:
                        fields_string.append(f"\t{line}")
                fields_string.append("")
            fields_string = "\n".join(fields_string)

        extra = ""
        if self.command == "help":
            extra = "\nAvailable commands:\n{}".format(
                  "\n".join(f" * {name}" for name in sorted(command.available_commands))
                )

        return f"{header}\n{'=' * len(header)}\n{doc}{fields_string}{extra}"

@command(name="discover")
class DiscoverCommand(Command):
    """
    Display information about all the devices that can be found on the network
    """
    finder = df.finder_field
    matcher = df.matcher_field
    refresh = df.refresh_field

    just_serials = dictobj.Field(sb.boolean, default=False
        , help = "Just return a list of serials instead of all the information per device"
        )

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher)

        if self.refresh is not None:
            fltr.force_refresh = self.refresh

        if self.just_serials:
            return await self.finder.serials(filtr=fltr)
        else:
            return await self.finder.info_for(filtr=fltr)

@command(name="query")
class QueryCommand(Command):
    """
    Send a pkt to devices and return the result
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field
    protocol_register = df.protocol_register_field

    multiple = dictobj.Field(sb.boolean, default=False
        , help = "Whether to expect multiple replies to our packet"
        )

    pkt_type = df.pkt_type_field
    pkt_args = df.pkt_args_field

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = chp.make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        script = self.target.script(msg)
        kwargs = {}
        if self.multiple:
            kwargs["multiple_replies"] = True
            kwargs["first_wait"] = 0.5
        return await chp.run(script, fltr, self.finder, timeout=self.timeout, **kwargs)

@command(name="transform")
class TransformCommand(Command):
    """
    Apply a http api like transformation to the lights
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field

    transform = dictobj.Field(sb.dictionary_spec(), wrapper=sb.required
        , help = """
            A dictionary of what options to use to transform the lights with.

            For example,
            ``{"power": "on", "color": "red"}``

            Or,
            ``{"color": "blue", "effect": "breathe", "cycles": 5}``
          """
        )

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = Transformer.using(self.transform)
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, add_replies=False, timeout=self.timeout)

@command(name="set")
class SetCommand(Command):
    """
    Send a pkt to devices. This is the same as query except res_required is False
    and results aren't returned
    """
    finder = df.finder_field
    target = df.target_field
    matcher = df.matcher_field
    timeout = df.timeout_field
    refresh = df.refresh_field
    protocol_register = df.protocol_register_field

    pkt_type = df.pkt_type_field
    pkt_args = df.pkt_args_field

    async def execute(self):
        fltr = chp.filter_from_matcher(self.matcher, self.refresh)
        msg = chp.make_message(self.protocol_register, self.pkt_type, self.pkt_args)
        msg.res_required = False
        script = self.target.script(msg)
        return await chp.run(script, fltr, self.finder, timeout=self.timeout)

@command(name="scene_info")
class SceneInfo(Command):
    """
    Retrieve information about scenes in the database
    """
    db_queue = df.db_queue_field

    uuids = dictobj.NullableField(sb.listof(sb.string_spec())
        , help = "Only get information for scene with these uuids"
        )

    async def execute(self):
        def get(db):
            info = defaultdict(list)
            fs = []
            if self.uuids:
                fs.append(Scene.uuid.in_(self.uuids))
            for scene in db.query(Scene).filter(*fs):
                dct = scene.as_dict()
                del dct["uuid"]
                info[scene.uuid].append(dct)
            return dict(info)
        return await self.db_queue.request(get)

@command(name="scene_change")
class SceneChange(Command):
    """
    Set all the options for a scene
    """
    db_queue = df.db_queue_field

    uuid = dictobj.NullableField(sb.string_spec
        , help = "The uuid of the scene to change, if None we create a new scene"
        )

    scene = dictobj.Field(sb.listof(Scene.DelayedSpec(storing=True))
        , help = "The options for the scene"
        )

    async def execute(self):
        def make(db):
            scene_uuid = self.uuid or str(uuid.uuid4())
            for thing in db.queries.get_scenes(uuid=scene_uuid):
                db.delete(thing)

            for part in self.scene:
                made = db.queries.create_scene(**part(scene_uuid).as_dict())
                db.add(made)

            return scene_uuid
        return await self.db_queue.request(make)

@command(name="scene_delete")
class SceneDelete(Command):
    """
    Set all the options for a scene
    """
    db_queue = df.db_queue_field

    uuid = dictobj.Field(sb.string_spec, wrapper=sb.required
        , help = "The uuid of the scene to delete"
        )

    async def execute(self):
        def delete(db):
            for thing in db.queries.get_scenes(uuid=self.uuid):
                db.delete(thing)

            return {"deleted": True}
        return await self.db_queue.request(delete)

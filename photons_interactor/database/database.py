from photons_interactor.database.connection import Base, DatabaseConnection

from photons_device_messages import DeviceMessages
from photons_multizone import MultiZoneMessages
from photons_tile_messages import TileMessages

from alembic.config import CommandLine as AlembicCommandLine, Config as AlembicConfig
from sqlalchemy import Column, Integer, String, Text, Boolean
from input_algorithms.errors import BadSpecValue
from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from alembic.script import ScriptDirectory
from sqlalchemy import pool
import pkg_resources
import shlex
import json
import sys
import os

class Database(dictobj.Spec):
    uri = dictobj.Field(sb.string_spec, wrapper=sb.required, formatted=True
        , help = "Uri to our database"
        )
    db_migrations = dictobj.Field(sb.overridden(os.path.join("{photons_interactor:resource}", "database", "migrations"))
        , format_into=sb.directory_spec
        )

async def migrate(database, extra=""):
    class Script(ScriptDirectory):
        def run_env(script):
            from alembic import context as alembic_context
            target_metadata = Base.metadata

            def run_migrations_offline():
                alembic_context.configure(url=database.uri, target_metadata=target_metadata, literal_binds=True)
                with alembic_context.begin_transaction():
                    alembic_context.run_migrations()

            def run_migrations_online():
                connectable = DatabaseConnection(database=database.uri, poolclass=pool.NullPool).engine
                with connectable.connect() as connection:
                    alembic_context.configure(connection=connection, target_metadata=target_metadata)
                    with alembic_context.begin_transaction():
                        alembic_context.run_migrations()

            if alembic_context.is_offline_mode():
                run_migrations_offline()
            else:
                run_migrations_online()

    def from_config(cfg):
        return Script(database.db_migrations)
    ScriptDirectory.from_config = from_config

    parts = []
    for p in sys.argv:
        if p == "--":
            break
        parts.append(p)

    commandline = AlembicCommandLine(prog=f"{' '.join(parts)} -- ")
    options = commandline.parser.parse_args(shlex.split(extra))
    if not hasattr(options, "cmd"):
        commandline.parser.error("too few arguments after the ' -- '")
    else:
        cfg = AlembicConfig(cmd_opts=options)
        commandline.run_cmd(cfg, options)

class range_spec(sb.Spec):
    def __init__(self, minimum, maximum, spec=None):
        self.minimum = minimum
        self.maximum = maximum
        self.spec = spec or sb.float_spec()

    def normalise_filled(self, meta, val):
        val = self.spec.normalise(meta, val)
        if val < self.minimum or val > self.maximum:
            raise BadSpecValue("Number must be between min and max", minimum=self.minimum, maximum=self.maximum, got=val, meta=meta)
        return val

class sized_list_spec(sb.Spec):
    def __init__(self, spec, length):
        self.spec = spec
        self.length = length

    def normalise_filled(self, meta, val):
        val = sb.listof(self.spec).normalise(meta, val)
        if len(val) != self.length:
            raise BadSpecValue("Expected certain number of parts", want=self.length, got=len(val), meta=meta)
        return val

class hsbk(sb.Spec):
    def __init__(self):
        self.specs = [
              range_spec(0, 360)
            , range_spec(0, 1)
            , range_spec(0, 1)
            , range_spec(2500, 9000, spec=sb.integer_spec())
            ]

    def normalise_filled(self, meta, val):
        val = sized_list_spec(sb.any_spec(), 4).normalise(meta, val)
        res = []
        for i, (v, s) in enumerate(zip(val, self.specs)):
            res.append(s.normalise(meta.at(i), v))
        return res

chain_spec = sized_list_spec(hsbk(), 64)

class json_string_spec(sb.Spec):
    def __init__(self, spec, storing):
        self.spec = spec
        self.storing = storing

    def normalise_filled(self, meta, val):
        if type(val) is str:
            try:
                v = json.loads(val)
            except (TypeError, ValueError) as error:
                raise BadSpecValue("Value was not valid json", error=error, meta=meta)
            else:
                normalised = self.spec.normalise(meta, v)
                if not self.storing:
                    return normalised

            return val
        else:
            v = self.spec.normalise(meta, val)
            if not self.storing:
                return v
            return json.dumps(v)

class Scene(Base):
    uuid = Column(String(64), nullable=True, index=True)
    matcher = Column(Text(), nullable=False)
    power = Column(Boolean(), nullable=True)
    color = Column(Text(), nullable=True)
    zones = Column(Text(), nullable=True)
    chain = Column(Text(), nullable=True)
    duration = Column(Integer(), nullable=True)

    __repr_columns__ = ("uuid", "matcher")

    def as_object(self):
        dct = {
              "uuid": self.uuid
            , "matcher": self.matcher
            , "power": self.power
            , "color": self.color
            , "zones": self.zones
            , "chain": self.chain
            , "duration": self.duration
            }
        return self.Spec(storing=False)().empty_normalise(**dct)

    def as_dict(self, ignore=None):
        return {k: v for k, v in self.as_object().as_dict().items() if v is not None and (ignore is None or k not in ignore)}

    @classmethod
    def Spec(kls, storing=True):
        class Fields(dictobj.Spec):
            uuid = dictobj.Field(sb.string_spec, wrapper=sb.required)
            matcher = dictobj.Field(json_string_spec(sb.dictionary_spec(), storing), wrapper=sb.required)
            power = dictobj.NullableField(sb.boolean)
            color = dictobj.NullableField(sb.string_spec)
            zones = dictobj.NullableField(json_string_spec(sb.listof(hsbk()), storing))
            chain = dictobj.NullableField(json_string_spec(sb.listof(chain_spec), storing))
            duration = dictobj.NullableField(sb.integer_spec)

            @property
            def transform_options(self):
                return {"power": "on" if self.power else "off", "color": self.color, "duration": self.duration}

            def colors_from_hsbks(self, hsbks, overrides):
                return [
                      { "hue": overrides.get("hue", h)
                      , "saturation": overrides.get("saturation", s)
                      , "brightness": overrides.get("brightness", b)
                      , "kelvin": overrides.get("kelvin", k)
                      } for h, s, b, k in hsbks
                    ]

            def zone_msgs(self, overrides):
                power = overrides.get("power", self.power)
                duration = overrides.get("duration", self.duration) or 0

                if power is not None:
                    level = 0 if power not in (True, "on") else 65535
                    yield DeviceMessages.SetLightPower(level=level, duration=duration)

                colors = self.colors_from_hsbks(self.zones, overrides)
                groups = []

                start = 0
                color = None
                i = -1
                while i < len(colors) - 1:
                    i += 1
                    if color is None:
                        color = colors[i]
                        continue
                    if colors[i] != color:
                        color = colors[i]
                        yield MultiZoneMessages.SetMultiZoneColorZones(start_index=start, end_index=i - 1, **color, duration=duration
                            , res_required = False
                            )
                        start = i

                color = colors[i]
                yield MultiZoneMessages.SetMultiZoneColorZones(start_index=start, end_index=i, **color, duration=duration
                    , res_required = False
                    )

            def chain_msgs(self, overrides):
                power = overrides.get("power", self.power)
                duration = overrides.get("duration", self.duration) or 0

                if power is not None:
                    level = 0 if power not in (True, "on") else 65535
                    yield DeviceMessages.SetLightPower(level=level, duration=duration)

                for i, lst in enumerate(self.chain):
                    colors = self.colors_from_hsbks(lst, overrides)
                    yield TileMessages.SetTileState64(tile_index=i, length=1, x=0, y=0, width=8, duration=duration, colors=colors
                        , res_required = False
                        )

        return Fields.FieldSpec

    @classmethod
    def DelayedSpec(kls, storing=True):
        spec = kls.Spec(storing=storing)()

        class delayed(sb.Spec):
            def normalise_filled(self, meta, val):
                val = sb.dictionary_spec().normalise(meta, val)

                def normalise(uuid):
                    if "uuid" in val:
                        del val["uuid"]
                    return spec.normalise(meta, {"uuid": uuid, **val})

                return normalise

        return delayed()

class SceneInfo(Base):
    uuid = Column(String(64), nullable=True, index=True, unique=True)
    label = Column(Text(), nullable=True)
    description = Column(Text(), nullable=True)

    def as_dict(self, ignore=None):
        dct = {"uuid": self.uuid, "label": self.label, "description": self.description}
        return {k: v for k, v in dct.items() if v is not None and (ignore is None or k not in ignore)}

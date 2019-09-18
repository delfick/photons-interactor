from photons_interactor.database.connection import Base, DatabaseConnection

from alembic.config import CommandLine as AlembicCommandLine, Config as AlembicConfig
from delfick_project.norms import dictobj, sb
from alembic.script import ScriptDirectory
from sqlalchemy import pool
import shlex
import sys
import os


class Database(dictobj.Spec):
    uri = dictobj.Field(
        sb.string_spec, wrapper=sb.required, formatted=True, help="Uri to our database"
    )
    db_migrations = dictobj.Field(
        sb.overridden(os.path.join("{photons_interactor:resource}", "database", "migrations")),
        format_into=sb.directory_spec,
    )


async def migrate(database, extra=""):
    class Script(ScriptDirectory):
        def run_env(script):
            from alembic import context as alembic_context

            target_metadata = Base.metadata

            def run_migrations_offline():
                alembic_context.configure(
                    url=database.uri, target_metadata=target_metadata, literal_binds=True
                )
                with alembic_context.begin_transaction():
                    alembic_context.run_migrations()

            def run_migrations_online():
                connectable = DatabaseConnection(
                    database=database.uri, poolclass=pool.NullPool
                ).engine
                with connectable.connect() as connection:
                    alembic_context.configure(
                        connection=connection, target_metadata=target_metadata
                    )
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


# And make all the models available so that the migrate command knows about them
from photons_interactor.database.models.scene_info import SceneInfo  # noqa
from photons_interactor.database.models.scene import Scene  # noqa

# And make vim quiet about unused imports
Scene = Scene
SceneInfo = SceneInfo

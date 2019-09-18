from photons_app.errors import PhotonsAppError

from delfick_project.norms import dictobj, sb
import subprocess
import shutil
import os


class Assets(dictobj.Spec):
    src = dictobj.Field(
        sb.overridden("{photons_interactor/static:resource}"),
        formatted=True,
        help="Folder where we can find the source of the assets",
    )

    @property
    def assets_folder(self):
        return os.path.join(self.src, "dist", "static")

    def ensure_npm(self):
        if not shutil.which("npm"):
            raise PhotonsAppError("Couldn't find npm, I suggest you use nvm...")

    @property
    def needs_install(self):
        return (
            not os.path.exists(os.path.join(self.src, "node_modules"))
            or os.environ.get("REBUILD") == 1
        )

    def run(self, *args, extra_env=None):
        env = dict(os.environ)
        if extra_env:
            env.update(extra_env)
        subprocess.check_call(["npm", *args], cwd=self.src, env=env)

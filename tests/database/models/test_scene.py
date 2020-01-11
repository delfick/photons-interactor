# coding: spec

from photons_interactor.database.test_helpers import DBTestRunner
from photons_interactor.database.models.scene import Scene

from photons_app.test_helpers import TestCase

from noseOfYeti.tokeniser.support import noy_sup_setUp, noy_sup_tearDown
from delfick_project.norms import Meta
import uuid

test_runner = DBTestRunner()

describe TestCase, "Scene":
    describe "DelayedSpec":
        it "returns a function that can be provided the uuid":
            identifier = str(uuid.uuid1())

            kwargs = dict(
                matcher={"label": "den"},
                power=True,
                color="red",
                zones=[[0, 0, 0, 3500], [1, 1, 1, 3500]],
                chain=None,
                duration=1,
            )

            scene = Scene.DelayedSpec(storing=False).normalise(Meta.empty(), kwargs)
            normalised = scene(identifier)

            expect = dict(kwargs)
            expect["uuid"] = identifier

            assert normalised.as_dict() == expect

            scene_for_storing = Scene.DelayedSpec(storing=True).normalise(Meta.empty(), kwargs)
            normalised = scene_for_storing(identifier)

            expect = dict(
                uuid=identifier,
                matcher='{"label": "den"}',
                power=True,
                color="red",
                zones="[[0.0, 0.0, 0.0, 3500], [1.0, 1.0, 1.0, 3500]]",
                chain=None,
                duration=1,
            )

            assert normalised.as_dict() == expect

    describe "Interaction with database":
        before_each:
            test_runner.before_each()
            self.database = test_runner.database

        after_each:
            test_runner.after_each()

        it "can store and retrieve from a spec":
            identifier = str(uuid.uuid1())

            chain = []
            for i in range(5):
                tile = []
                for j in range(64):
                    tile.append([j, 0, 1, 3500])
                chain.append(tile)

            kwargs = dict(
                uuid=identifier,
                matcher={"label": "den"},
                power=True,
                color="red",
                zones=[[0, 0, 0, 3500], [1, 1, 1, 3500]],
                chain=chain,
                duration=1,
            )

            scene = Scene.Spec(storing=True).empty_normalise(**kwargs)
            self.database.add(self.database.queries.create_scene(**scene))
            self.database.commit()

            got = self.database.queries.get_one_scene(uuid=identifier)
            assert got.as_dict() == kwargs

            obj = got.as_object()
            for prop in kwargs.keys():
                assert getattr(obj, prop) == kwargs[prop]

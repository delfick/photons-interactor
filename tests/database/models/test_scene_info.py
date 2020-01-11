# coding: spec

from photons_interactor.database.models.scene_info import SceneInfo
from photons_interactor.database.test_helpers import DBTestRunner

from photons_app.test_helpers import TestCase

from noseOfYeti.tokeniser.support import noy_sup_setUp, noy_sup_tearDown
from delfick_project.norms import Meta
import sqlalchemy.exc
import uuid

test_runner = DBTestRunner()

describe TestCase, "SceneInfo":
    it "can return itself as a dict":
        info = SceneInfo(uuid="one", label=None, description=None)
        assert info.as_dict() == {"uuid": "one"}

        info = SceneInfo(uuid="two", label="kitchen", description=None)
        assert info.as_dict() == {"uuid": "two", "label": "kitchen"}

        info = SceneInfo(uuid="three", label="bathroom", description="blah")
        assert info.as_dict() == {"uuid": "three", "label": "bathroom", "description": "blah"}

    describe "Interaction with database":
        before_each:
            test_runner.before_each()
            self.database = test_runner.database

        after_each:
            test_runner.after_each()

        it "Must have unique uuid":
            identifier = str(uuid.uuid1())

            kwargs = dict(uuid=identifier, label="blah", description="described")

            info = self.database.queries.create_scene_info(**kwargs)
            self.database.add(info)
            self.database.commit()

            info2 = self.database.queries.create_scene_info(**kwargs)
            self.database.add(info2)
            try:
                with self.fuzzyAssertRaisesError(sqlalchemy.exc.IntegrityError):
                    self.database.commit()
            finally:
                self.database.rollback()

            info3 = self.database.queries.create_scene_info(uuid=identifier)
            self.database.add(info3)
            try:
                with self.fuzzyAssertRaisesError(sqlalchemy.exc.IntegrityError):
                    self.database.commit()
            finally:
                self.database.rollback()

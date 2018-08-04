# coding: spec

from photons_interactor.database.connection import DatabaseConnection, Base

from photons_app.formatter import MergedOptionStringFormatter
from photons_app.test_helpers import TestCase
from photons_app import helpers as hp

from noseOfYeti.tokeniser.support import noy_sup_setUp, noy_sup_tearDown
from sqlalchemy import Column, String, Boolean
import sqlalchemy.exc
import tempfile
import os

Test = None

def setUp():
    global Test

    class Test(Base):
        one = Column(String(64), nullable=True, unique=True)
        two = Column(Boolean(), nullable=True)

        __repr_columns__ = ("one", "two")

        def as_dict(self):
            return {"one": self.one, "two": self.two}

def tearDown():
    del Base._decl_class_registry["Test"]
    tables = dict(Base.metadata.tables)
    del tables["test"]
    Base.metadata.tables = tables

describe TestCase, "DatabaseConnection":
    before_each:
        self.tmpfile = tempfile.NamedTemporaryFile(delete=False)
        self.filename = self.tmpfile.name
        self.database = DatabaseConnection(database=f"sqlite:///{self.filename}").new_session()
        self.database.create_tables()

    after_each:
        # Cleanup
        if hasattr(self, "tmpfile") and self.tmpfile is not None:
            self.tmpfile.close()
        if hasattr(self, "filename") and self.filename and os.path.exists(self.filename):
            os.remove(self.filename)
        if hasattr(self, "database"):
            self.database.close()

    describe "actions":
        it "can create and query the database and delete from the database":
            self.database.add(Test(one="one", two=True))
            self.database.add(Test(one="two", two=False))
            self.database.commit()

            made = self.database.query(Test).order_by(Test.one.asc()).all()
            self.assertEqual([t.as_dict() for t in made]
                , [ Test(one="one", two=True).as_dict()
                  , Test(one="two", two=False).as_dict()
                  ]
                )

            self.database.delete(made[0])
            self.database.commit()

            made = self.database.query(Test).order_by(Test.one.asc()).all()
            self.assertEqual([t.as_dict() for t in made]
                , [ Test(one="two", two=False).as_dict()
                  ]
                )

        it "can refresh items":
            one = Test(one="one", two=True)
            self.database.add(one)
            self.database.commit()

            made = self.database.query(Test).one()
            made.two = False
            self.database.add(made)
            self.database.commit()

            self.database.refresh(one)
            self.assertEqual(one.two, False)

        it "can rollback":
            one = Test(one="one", two="wat")
            self.database.add(one)
            try:
                self.database.commit()
            except sqlalchemy.exc.StatementError:
                self.database.rollback()

            one = Test(one="one", two=True)
            self.database.add(one)
            self.database.commit()

            made = self.database.query(Test).one()
            self.assertEqual(made.as_dict(), one.as_dict())

        it "can execute against the database":
            one = Test(one="one", two=True)
            self.database.add(one)
            self.database.commit()

            result = list(self.database.execute("SELECT * FROM test WHERE one=:one", {"one": "one"}))
            self.assertEqual(result, [(1, "one", 1)])

    describe "queries":
        it "has methods for doing stuff with the database":
            one = self.database.queries.create_test(one="one", two=True)
            self.database.add(one)
            self.database.commit()

            two, made = self.database.queries.get_or_create_test(one="one", two=True)
            self.assertEqual(made, False)
            self.assertEqual(one.id, two.id)

            three, made = self.database.queries.get_or_create_test(one="two", two=True)
            self.assertEqual(made, True)
            self.database.add(three)
            self.database.commit()

            made = self.database.queries.get_tests().order_by(Test.one.asc()).all()
            self.assertEqual([t.as_dict() for t in made], [t.as_dict() for t in (one, three)])

            one_got = self.database.queries.get_test(one="one")
            self.assertEqual(one_got.as_dict(), one.as_dict())
            self.assertEqual(one_got.id, one.id)

            with self.fuzzyAssertRaisesError(sqlalchemy.orm.exc.MultipleResultsFound):
                self.database.queries.get_one_test(two=True)

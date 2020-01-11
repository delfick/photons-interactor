# coding: spec

from photons_interactor.database.test_helpers import DBTestRunner
from photons_interactor.database.connection import Base

from photons_app.test_helpers import TestCase
from photons_app import helpers as hp

from noseOfYeti.tokeniser.support import noy_sup_setUp, noy_sup_tearDown
from sqlalchemy import Column, String, Boolean
import sqlalchemy.exc

Test = None
test_runner = DBTestRunner()


def setup_module():
    global Test

    class Test(Base):
        one = Column(String(64), nullable=True, unique=True)
        two = Column(Boolean(), nullable=True)

        __repr_columns__ = ("one", "two")

        def as_dict(self):
            return {"one": self.one, "two": self.two}


def teardown_module():
    del Base._decl_class_registry["Test"]
    tables = dict(Base.metadata.tables)
    del tables["test"]
    Base.metadata.tables = tables


describe TestCase, "DatabaseConnection":
    before_each:
        test_runner.before_each(start_db_queue=False)
        self.database = test_runner.database

    after_each:
        test_runner.after_each()

    describe "actions":
        it "can create and query the database and delete from the database":
            self.database.add(Test(one="one", two=True))
            self.database.add(Test(one="two", two=False))
            self.database.commit()

            made = self.database.query(Test).order_by(Test.one.asc()).all()
            assert [t.as_dict() for t in made] == [
                Test(one="one", two=True).as_dict(),
                Test(one="two", two=False).as_dict(),
            ]

            self.database.delete(made[0])
            self.database.commit()

            made = self.database.query(Test).order_by(Test.one.asc()).all()
            assert [t.as_dict() for t in made] == [Test(one="two", two=False).as_dict()]

        it "can refresh items":
            one = Test(one="one", two=True)
            self.database.add(one)
            self.database.commit()

            made = self.database.query(Test).one()
            made.two = False
            self.database.add(made)
            self.database.commit()

            self.database.refresh(one)
            assert one.two == False

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
            assert made.as_dict() == one.as_dict()

        it "can execute against the database":
            one = Test(one="one", two=True)
            self.database.add(one)
            self.database.commit()

            result = list(
                self.database.execute("SELECT * FROM test WHERE one=:one", {"one": "one"})
            )
            assert result == [(1, "one", 1)]

    describe "queries":
        it "has methods for doing stuff with the database":
            one = self.database.queries.create_test(one="one", two=True)
            self.database.add(one)
            self.database.commit()

            two, made = self.database.queries.get_or_create_test(one="one", two=True)
            assert made == False
            assert one.id == two.id

            three, made = self.database.queries.get_or_create_test(one="two", two=True)
            assert made == True
            self.database.add(three)
            self.database.commit()

            made = self.database.queries.get_tests().order_by(Test.one.asc()).all()
            assert [t.as_dict() for t in made] == [t.as_dict() for t in (one, three)]

            one_got = self.database.queries.get_test(one="one")
            assert one_got.as_dict() == one.as_dict()
            assert one_got.id == one.id

            with self.fuzzyAssertRaisesError(sqlalchemy.orm.exc.MultipleResultsFound):
                self.database.queries.get_one_test(two=True)

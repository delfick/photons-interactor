# coding: spec

from photons_interactor.database.test_helpers import DBTestRunner
from photons_interactor.database.connection import Base

from photons_app.test_helpers import AsyncTestCase
from photons_app.errors import PhotonsAppError

from noseOfYeti.tokeniser.async_support import async_noy_sup_setUp, async_noy_sup_tearDown
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


describe AsyncTestCase, "DatabaseConnection":
    async before_each:
        test_runner.before_each(start_db_queue=True)
        self.db_queue = test_runner.db_queue

    async after_each:
        test_runner.after_each()
        await test_runner.after_each_db_queue()

    async it "can execute queries":

        def do_set(db):
            one = db.queries.create_test(one="one", two=True)
            db.add(one)

        await self.wait_for(self.db_queue.request(do_set))

        def do_get(db):
            return db.queries.get_one_test().as_dict()

        got = await self.wait_for(self.db_queue.request(do_get))
        self.assertEqual(got, {"one": "one", "two": True})

    async it "retries on OperationalError":
        tries = [True, True]

        def do_error(db):
            tries.pop(0)
            raise sqlalchemy.exc.OperationalError("select", {}, "")

        with self.fuzzyAssertRaisesError(sqlalchemy.exc.OperationalError):
            await self.wait_for(self.db_queue.request(do_error))

        self.assertEqual(tries, [])

    async it "can work after the first OperationalError":
        tries = [True, True]

        def do_error(db):
            tries.pop(0)
            if len(tries) == 1:
                raise sqlalchemy.exc.OperationalError("select", {}, "")
            else:
                one = db.queries.create_test(one="one", two=True)
                db.add(one)

        await self.wait_for(self.db_queue.request(do_error))

        def do_get(db):
            return db.queries.get_one_test().as_dict()

        got = await self.wait_for(self.db_queue.request(do_get))
        self.assertEqual(got, {"one": "one", "two": True})

        self.assertEqual(tries, [])

    async it "does not retry other errors":
        errors = [sqlalchemy.exc.InvalidRequestError(), PhotonsAppError("blah"), ValueError("nope")]

        for error in errors:
            tries = [True]

            def do_error(db):
                tries.pop(0)
                raise error

            with self.fuzzyAssertRaisesError(type(error)):
                await self.wait_for(self.db_queue.request(do_error))
            self.assertEqual(tries, [])

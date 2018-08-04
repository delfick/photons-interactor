# coding: spec

from photons_interactor.database.connection import DatabaseConnection, Base
from photons_interactor.database.db_queue import DBQueue

from photons_app.formatter import MergedOptionStringFormatter
from photons_app.test_helpers import AsyncTestCase
from photons_app.errors import PhotonsAppError
from photons_app import helpers as hp

from noseOfYeti.tokeniser.async_support import async_noy_sup_setUp, async_noy_sup_tearDown
from sqlalchemy import Column, String, Boolean
import sqlalchemy.exc
import tempfile
import asyncio
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

describe AsyncTestCase, "DatabaseConnection":
    async before_each:
        self.tmpfile = tempfile.NamedTemporaryFile(delete=False)
        self.filename = self.tmpfile.name
        uri = f"sqlite:///{self.filename}"
        self.database = DatabaseConnection(database=uri).new_session()
        self.database.create_tables()
        self.final_future = asyncio.Future()
        self.db_queue = DBQueue(self.final_future, 5, lambda exc: 1, uri)
        self.db_queue.start()

    async after_each:
        # Cleanup
        if hasattr(self, "final_future"):
            self.final_future.cancel()
        if hasattr(self, "tmpfile") and self.tmpfile is not None:
            self.tmpfile.close()
        if hasattr(self, "filename") and self.filename and os.path.exists(self.filename):
            os.remove(self.filename)
        if hasattr(self, "database"):
            self.database.close()
        if hasattr(self, "db_queue"):
            await self.db_queue.finish()

            # Stop annoying loop was closed warnings
            import threading
            for thread in threading.enumerate()[1:]:
                thread.join()

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
        errors = [
              sqlalchemy.exc.InvalidRequestError()
            , PhotonsAppError("blah")
            , ValueError("nope")
            ]

        for error in errors:
            tries = [True]

            def do_error(db):
                tries.pop(0)
                raise error
            with self.fuzzyAssertRaisesError(type(error)):
                await self.wait_for(self.db_queue.request(do_error))
            self.assertEqual(tries, [])

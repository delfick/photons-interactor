from photons_interactor.database.connection import DatabaseConnection
from photons_interactor.database.db_queue import DBQueue

import threading
import tempfile
import asyncio
import os

class DBTestRunner:
    def before_each(self, start_db_queue=False):
        self.tmpfile = tempfile.NamedTemporaryFile(delete=False)
        self.filename = self.tmpfile.name
        uri = f"sqlite:///{self.filename}"
        self.database = DatabaseConnection(database=uri).new_session()
        self.database.create_tables()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.final_future = asyncio.Future()

        if start_db_queue:
            self.db_queue = DBQueue(self.final_future, 5, lambda exc: 1, uri)
            self.db_queue.start()

    def after_each(self):
        if hasattr(self, "final_future"):
            self.final_future.cancel()
        if hasattr(self, "tmpfile") and self.tmpfile is not None:
            self.tmpfile.close()
        if hasattr(self, "filename") and self.filename and os.path.exists(self.filename):
            os.remove(self.filename)
        if hasattr(self, "database"):
            self.database.close()

    async def after_each_db_queue(self):
        if hasattr(self, "db_queue"):
            await self.db_queue.finish()

            # Stop annoying loop was closed warnings
            for thread in threading.enumerate()[1:]:
                thread.join()

# coding: spec

from photons_interactor.commander.decorator import command_spec, command
from photons_interactor.commander import test_helpers as cthp
from photons_interactor.commander import default_fields as df
from photons_interactor.commander.commands import Command
from photons_interactor.commander import Commander

from photons_app.test_helpers import AsyncTestCase

from noseOfYeti.tokeniser.async_support import async_noy_sup_setUp
from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb
from unittest import mock

describe AsyncTestCase, "Commander":
    async it "takes in some things":
        finder = mock.Mock(nme="finder")
        db_queue = mock.Mock(name="db_queue")
        target_register = mock.Mock(name="target_register")
        protocol_register = mock.Mock(name="protocol_register")

        device = cthp.Device("d073d5000001", None
            , label = "kitchen"
            , power = 0
            , group = cthp.Group("one", "one", 0)
            , location = cthp.Group("one", "one", 0)
            , color = cthp.Color(0, 1, 1, 2500)
            , vendor_id = 1
            , product_id = 31
            , firmware = cthp.Firmware("2.75", 1521690429)
            )
        test_devices = {"devices": [device]}

        commander = Commander(
              finder = finder
            , target_register = target_register
            , protocol_register = protocol_register
            , db_queue = db_queue
            , test_devices = test_devices
            )

        meta_everything = commander.meta.everything
        self.assertIs(meta_everything["finder"], finder)
        self.assertEqual(meta_everything["test_devices"]["devices"], test_devices["devices"])
        self.assertIs(meta_everything["db_queue"], db_queue)
        self.assertIs(meta_everything["target_register"], target_register)
        self.assertIs(meta_everything["protocol_register"], protocol_register)
        self.assertIs(meta_everything["commander"], commander)

        self.assertIs(type(commander.command_spec), command_spec)

    describe "execute":
        async before_each:
            self.finder = mock.Mock(name="finder")
            self.db_queue = mock.Mock(name="db_queue")
            self.target_register = mock.Mock(name="target_register")
            self.protocol_register = mock.Mock(name="protocol_register")

            self.commander = Commander(
                  finder = self.finder
                , target_register = self.target_register
                , protocol_register = self.protocol_register
                , db_queue = self.db_queue
                )

            self.progress_messages = []

            def progress(message):
                self.progress_messages.append(message)
            self.progress = progress

        async it "can execute a command":
            res = mock.Mock(name="res")

            class Cmd(Command):
                async def execute(self):
                    return res

            self.assertIs(await self.wait_for(self.commander.execute(Cmd(), self.progress)), res)

        async it "request future gets cancelled on error":
            res = mock.Mock(name="res")

            got = []

            class Cmd(Command):
                request_future = df.request_future_field

                async def execute(s):
                    assert not s.request_future.done()
                    got.append(s.request_future)
                    raise Exception("Nope")

            with self.fuzzyAssertRaisesError(Exception, "Nope"):
                with mock.patch.object(command, "available_commands", {}):
                    command(name="thing")(Cmd)
                    await self.wait_for(self.commander.execute({"command": "thing"}, self.progress))

            assert got[0].cancelled()

        async it "it can have extra options":
            finder = mock.Mock(name="finder")
            other = mock.Mock(name="other")

            got = []

            class Cmd(Command):
                finder = df.finder_field
                protocol_register = df.protocol_register_field

                other = dictobj.Field(sb.overridden("{other}"), formatted=True)

                async def execute(s):
                    return s

            with mock.patch.object(command, "available_commands", {}):
                command(name="thing")(Cmd)
                cmd = await self.wait_for(
                      self.commander.execute(
                          {"command": "thing"}
                        , self.progress
                        , {"finder": finder, "other": other}
                        )
                    )

            self.assertIs(cmd.finder, finder)
            self.assertIs(cmd.protocol_register, self.protocol_register)
            self.assertIs(cmd.other, other)

        async it "can format a dictionary into a command":
            res = mock.Mock(name="res")
            target = mock.Mock(name="target")
            self.target_register.resolve.return_value = target

            class Cmd(Command):
                finder = df.finder_field
                target = df.target_field
                db_queue = df.db_queue_field
                commander = df.commander_field
                progress_cb = df.progress_cb_field
                request_future = df.request_future_field
                protocol_register = df.protocol_register_field
                one = dictobj.Field(sb.integer_spec)

                async def execute(s):
                    assert not s.request_future.done()
                    s.progress_cb("hello")
                    return s, res

            with mock.patch.object(command, "available_commands", {}):
                command(name="thing")(Cmd)
                cmd, r = await self.wait_for(self.commander.execute({"command": "thing", "args": {"one": 1}}, self.progress))

            self.assertIs(r, res)

            self.assertIs(type(cmd), Cmd)
            self.assertIs(cmd.finder, self.finder)
            self.assertIs(cmd.target, target)
            self.assertIs(cmd.protocol_register, self.protocol_register)
            self.assertIs(cmd.progress_cb, self.progress)
            assert cmd.request_future.cancelled()
            self.assertIs(cmd.db_queue, self.db_queue)
            self.assertIs(cmd.one, 1)
            self.assertIs(cmd.commander, self.commander)
            self.assertEqual(self.progress_messages, ["hello"])

            self.target_register.resolve.assert_called_once_with("lan")

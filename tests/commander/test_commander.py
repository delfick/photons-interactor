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

        commander = Commander(finder, target_register, protocol_register, db_queue, test_devices)

        meta_everything = commander.meta.everything
        self.assertIs(meta_everything["finder"], finder)
        self.assertEqual(meta_everything["test_devices"]["devices"], test_devices["devices"])
        self.assertIs(meta_everything["db_queue"], db_queue)
        self.assertIs(meta_everything["target_register"], target_register)
        self.assertIs(meta_everything["protocol_register"], protocol_register)

        self.assertIs(type(commander.command_spec), command_spec)

    describe "execute":
        async before_each:
            self.finder = mock.Mock(name="finder")
            self.db_queue = mock.Mock(name="db_queue")
            self.target_register = mock.Mock(name="target_register")
            self.protocol_register = mock.Mock(name="protocol_register")

            self.commander = Commander(self.finder, self.target_register, self.protocol_register, self.db_queue)

        async it "can execute a command":
            res = mock.Mock(name="res")

            class Cmd(Command):
                async def execute(self):
                    return res

            self.assertIs(await self.wait_for(self.commander.execute(Cmd())), res)

        async it "can format a dictionary into a command":
            res = mock.Mock(name="res")
            target = mock.Mock(name="target")
            self.target_register.resolve.return_value = target

            class Cmd(Command):
                finder = df.finder_field
                target = df.target_field
                protocol_register = df.protocol_register_field
                db_queue = df.db_queue_field
                one = dictobj.Field(sb.integer_spec)

                async def execute(self):
                    return self, res

            with mock.patch.object(command, "available_commands", {}):
                command(name="thing")(Cmd)
                cmd, r = await self.wait_for(self.commander.execute({"command": "thing", "args": {"one": 1}}))

            self.assertIs(r, res)

            self.assertIs(type(cmd), Cmd)
            self.assertIs(cmd.finder, self.finder)
            self.assertIs(cmd.target, target)
            self.assertIs(cmd.protocol_register, self.protocol_register)
            self.assertIs(cmd.db_queue, self.db_queue)
            self.assertIs(cmd.one, 1)

            self.target_register.resolve.assert_called_once_with("lan")

# coding: spec

from photons_interactor.commander.commands.animations import AnimationsStore
from photons_interactor.commander.store import store

from photons_app import helpers as hp

from photons_messages import protocol_register

from unittest import mock
import asynctest
import pytest


@pytest.fixture(scope="module")
def V():
    class V:
        afr = mock.Mock(name="afr")
        db_queue = mock.Mock(name="db_queue")
        commander = mock.Mock(name="commander")

        @hp.memoized_property
        def lan_target(s):
            m = mock.Mock(name="lan_target")

            m.args_for_run = asynctest.mock.CoroutineMock(name="args_for_run", return_value=s.afr)
            m.close_args_for_run = asynctest.mock.CoroutineMock(name="close_args_for_run")

            return m

        @hp.memoized_property
        def finder(s):
            finder = mock.Mock(name="finder")
            finder.start = asynctest.mock.CoroutineMock(name="start")
            finder.finish = asynctest.mock.CoroutineMock(name="finish")
            return finder

        @hp.memoized_property
        def FakeDeviceFinder(s):
            return mock.Mock(name="DeviceFinder", return_value=s.finder)

        @hp.memoized_property
        def FakeDBQueue(s):
            return mock.Mock(name="DBQueue", return_value=s.db_queue)

        @hp.memoized_property
        def FakeCommander(s):
            return mock.Mock(name="Commander", return_value=s.commander)

        @hp.memoized_property
        def target_register(s):
            m = mock.Mock(name="target_register")

            def resolve(name):
                if name == "lan":
                    return s.lan_target
                else:
                    assert False, f"Unknown target: {name}"

            m.resolve.side_effect = resolve
            return m

    return V()


@pytest.fixture(scope="module")
async def wrapper(V, server_wrapper):
    commander_patch = mock.patch("photons_interactor.server.Commander", V.FakeCommander)
    db_patch = mock.patch("photons_interactor.server.DBQueue", V.FakeDBQueue)
    finder_patch = mock.patch("photons_interactor.server.DeviceFinder", V.FakeDeviceFinder)

    with commander_patch, db_patch, finder_patch:
        kwargs = {
            "target_register": V.target_register,
            "device_finder_options": {"arg1": 0.1, "arg2": True},
        }
        async with server_wrapper(store, **kwargs) as wrapper:
            yield wrapper


@pytest.fixture(autouse=True)
async def wrap_tests(wrapper):
    async with wrapper.test_wrap():
        yield


@pytest.fixture()
def runner(wrapper):
    return wrapper.runner


@pytest.fixture()
def server(wrapper):
    return wrapper.server


describe "Server":
    async it "has an index page", asserter, runner:

        class HTML:
            def __eq__(s, other):
                return other.startswith(b"<!DOCTYPE html>")

        await runner.assertGET(asserter, "/", text_output=HTML())

    async it "can execute commands", V, runner:
        V.commander.executor.return_value.execute = asynctest.mock.CoroutineMock(
            name="execute", return_value={}
        )

    async it "starts things correctly", V, server, runner:
        assert server.finder is V.finder
        assert isinstance(server.animations, AnimationsStore)

        V.FakeCommander.assert_called_once_with(
            store,
            finder=V.finder,
            db_queue=V.db_queue,
            arranger=server.arranger,
            animations=server.animations,
            test_devices=None,
            final_future=runner.final_future,
            server_options=server.server_options,
            target_register=V.target_register,
            protocol_register=protocol_register,
        )
        V.FakeDeviceFinder.assert_called_once_with(V.lan_target, arg1=0.1, arg2=True)
        V.FakeDBQueue.assert_called_once_with(
            runner.final_future, 5, mock.ANY, "sqlite:///:memory:"
        )

        V.target_register.resolve.assert_called_once_with("lan")
        V.finder.start.assert_called_once_with()
        V.db_queue.start.assert_called_once_with()

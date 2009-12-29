#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright Bernardo Heynemann <heynemann@gmail.com>

# Licensed under the Open Software License ("OSL") v. 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.opensource.org/licenses/osl-3.0.php

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os

from fudge import Fake, with_fakes, with_patched_object, clear_expectations
from fudge.inspector import arg
import skink.lib
import ion.controllers as ctrl

import ion
from ion import Server, ServerStatus, Context
from ion.controllers import Controller, route

def clear():
    ctrl.__CONTROLLERS__ = []
    ctrl.__CONTROLLERSDICT__ = {}

fake_import_controllers = Fake(callable=True)
fake_test_db = Fake(callable=True)
custom_run_server = Fake(callable=True)

def test_server_status_statuses():
    assert ServerStatus.Unknown == 0
    assert ServerStatus.Starting == 1
    assert ServerStatus.Started == 2
    assert ServerStatus.Stopping == 3
    assert ServerStatus.Stopped == 4

def test_server_should_have_unknown_status_by_default():
    server = Server(root_dir="some")
    assert server.status == ServerStatus.Unknown

def test_server_keeps_root_dir():
    server = Server(root_dir="some_other")
    assert server.root_dir == "some_other"

@with_fakes
@with_patched_object(Server, "run_server", custom_run_server)
@with_patched_object(Server, "import_controllers", fake_import_controllers)
def test_server_should_start():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = default_context
    server.start(config_path="config.ini")

    assert server.status == ServerStatus.Started

def test_server_should_have_context():
    clear_expectations()
    server = Server(root_dir="some")

    assert server.context

def test_server_should_have_context_of_type_context():
    clear_expectations()
    server = Server(root_dir="some")

    assert isinstance(server.context, Context)

context = Fake('context').has_attr(bus=Fake('bus'))
context.bus.expects('subscribe').with_args("anything", arg.any_value())

@with_fakes
@with_patched_object(Server, "run_server", custom_run_server)
def test_server_subscribe_calls_bus_subscribe():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = context

    server.subscribe('anything', lambda server, bus, arguments: None)

default_context = Fake('context').has_attr(bus=Fake('bus'))
default_context.bus.expects('publish').with_args("on_before_server_start", arg.any_value())
default_context.bus.next_call(for_method='publish').with_args("on_after_server_start", arg.any_value())
default_context.expects('load_settings').with_args(arg.endswith('/some/config.ini'))

@with_fakes
@with_patched_object(Server, "run_server", custom_run_server)
@with_patched_object(Server, "import_controllers", fake_import_controllers)
def test_server_start_should_publish_on_before_and_after_server_start_event():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = default_context

    server.start("config.ini")

@with_fakes
@with_patched_object(Server, "run_server", custom_run_server)
@with_patched_object(Server, "import_controllers", fake_import_controllers)
def test_server_start_calls_run_server():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = default_context

    server.start("config.ini")

settings_context = Fake('context').has_attr(settings=Fake('settings'))
settings_context.settings.has_attr(Ion=Fake('ion'))
settings_context.settings.Ion.has_attr(host="somehost", port="4728", baseurl="http://some.url:4728", verbose="True")
def test_get_server_settings():
    clear()
    server = Server(root_dir="some", context=settings_context)

    server_settings = server.get_server_settings()
    assert server_settings
    expected_settings = {
                   'server.socket_host': "somehost",
                   'server.socket_port': 4728,
                   'request.base': "http://some.url:4728",
                   'tools.encode.on': True, 
                   'tools.encode.encoding': 'utf-8',
                   'tools.decode.on': True,
                   'tools.trailing_slash.on': True,
                   'log.screen': True,
                   'tools.sessions.on': True,
                   'tools.storm.on': True
               }

    assert server_settings == expected_settings

def test_get_mounts():
    clear()
    server = Server(root_dir="some", context=settings_context)

    mounts = server.get_mounts("dispatcher")

    assert mounts

    expected = {
            '/': {
                'request.dispatch': "dispatcher",
                'tools.staticdir.root': "some/skink/",
            },
            '/media': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'media'
            }
        }

    assert mounts == expected

routes_dispatcher = Fake("routes_dispatcher")
custom_dispatch = Fake('dispatcher').has_attr(RoutesDispatcher=Fake(callable=True).returns(routes_dispatcher))
@with_fakes
@with_patched_object("cherrypy", "dispatch", custom_dispatch)
def test_get_dispatcher():
    clear()
    server = Server(root_dir="some", context=None)

    dispatcher = server.get_dispatcher()

    assert dispatcher
    assert dispatcher == routes_dispatcher

@with_fakes
@with_patched_object("cherrypy", "dispatch", custom_dispatch)
def test_get_dispatcher_calls_controllers_and_fills_context():
    clear()

    class TestDispatchedController(Controller):
        pass

    server = Server(root_dir="some", context=None)

    dispatcher = server.get_dispatcher()

    assert dispatcher
    assert dispatcher == routes_dispatcher


fake_get_server_settings = Fake(callable=True).returns({"some":"settings"})
fake_get_dispatcher = Fake(callable=True).returns("dispatcher")
fake_get_mounts = Fake(callable=True).with_args("dispatcher").returns("mounts")

custom_config = Fake('config')
custom_config.expects('update').with_args({"some":"settings"})

fake_tree = Fake('tree')
fake_tree.expects('mount').with_args(None, config="mounts").returns("app")

fake_engine = Fake("engine")
fake_engine.expects('subscribe').with_args('start_thread', arg.any_value())
fake_engine.next_call('subscribe').with_args('stop_thread', arg.any_value())

fake_engine.expects('start')
fake_engine.expects('block')

@with_fakes
@with_patched_object("cherrypy", "config", custom_config)
@with_patched_object("cherrypy", "tree", fake_tree)
@with_patched_object("cherrypy", "engine", fake_engine)
@with_patched_object(Server, "get_server_settings", fake_get_server_settings)
@with_patched_object(Server, "get_dispatcher", fake_get_dispatcher)
@with_patched_object(Server, "get_mounts", fake_get_mounts)
@with_patched_object(Server, "import_controllers", fake_import_controllers)
@with_patched_object(Server, "test_connection", fake_test_db)
def test_run_server_updates_config_and_starts_cherrypy():
    clear()

    server = Server(root_dir="some", context=None)

    server.run_server()

    assert server.app
    assert server.app == "app"

stop_context = Fake('context').has_attr(bus=Fake('bus'))
stop_context.bus.expects('publish').with_args("on_before_server_stop", arg.any_value())
stop_context.bus.next_call(for_method='publish').with_args("on_after_server_stop", arg.any_value())

stop_engine_fake = Fake('engine')
stop_engine_fake.expects('exit')

@with_fakes
@with_patched_object('cherrypy', "engine", stop_engine_fake)
def test_server_stop_should_publish_on_before_and_after_server_stop_event():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = stop_context

    server.stop()

fake_db = Fake('db')
fake_db.expects('connect')
fake_db.expects('disconnect')
db_engine = Fake(callable=True).with_args(None).returns(fake_db)

@with_fakes
@with_patched_object(ion.server, "Db", db_engine)
def test_server_test_connection():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = None

    server.test_connection()

fake_db2 = Fake('db')
fake_db2.expects('connect')
fake_db2.has_attr(store="store")
db_engine2 = Fake(callable=True).with_args(None).returns(fake_db2)
fake_thread_data = Fake('thread_data')
@with_fakes
@with_patched_object(ion.server, "Db", db_engine2)
@with_patched_object(ion.server, "thread_data", fake_thread_data)
def test_server_connect_db():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = None

    server.connect_db(1)

    assert server.storm_stores[1] == "store"

fake_log = Fake(callable=True).with_args("Cleaning up store.", "STORM")
fake_db3 = Fake('db')
fake_db3.expects('disconnect')
fake_store = Fake('store')
fake_store.expects('close')
@with_fakes
@with_patched_object(ion.server.cherrypy, "log", fake_log)
def test_server_disconnect_db():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = None
    server.db = fake_db3
    server.storm_stores[1] = fake_store

    server.disconnect_db(1)

fake_log2 = Fake(callable=True).with_args("Could not find store.", "STORM")
fake_db4 = Fake('db')
fake_db4.expects('disconnect')
@with_fakes
@with_patched_object(ion.server.cherrypy, "log", fake_log2)
def test_server_disconnect_db_logs_when_no_store_found():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = None
    server.db = fake_db4

    server.disconnect_db(1)

import_context2 = Fake('context').has_attr(settings=Fake('settings'))
import_context2.settings.has_attr(Ion=Fake('ion'))
import_context2.settings.Ion.has_attr(controllers_path="/controllers")
fake_sys_path = Fake('syspath')
fake_sys_path.expects('append').with_args(arg.endswith('/some/controllers'))
fake_os_list_dir = Fake(callable=True).with_args(arg.endswith('/some/controllers')).returns(['somefile.py'])
fake_imp = Fake(callable=True).with_args("somefile")
@with_fakes
@with_patched_object(sys, "path", fake_sys_path)
@with_patched_object(os, "listdir", fake_os_list_dir)
@with_patched_object(Server, "imp", fake_imp)
def test_server_imports_controllers():
    clear()
    server = Server(root_dir="some", context=import_context2)

    server.import_controllers()


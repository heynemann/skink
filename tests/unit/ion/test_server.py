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

from fudge import Fake, with_fakes, with_patched_object, clear_expectations
from fudge.inspector import arg

import skink.lib.ion.controllers as ctrl
from skink.lib.ion import Server, ServerStatus, Context
from skink.lib.ion.controllers import Controller, route

def clear():
    ctrl.__CONTROLLERS__ = []
    ctrl.__CONTROLLERSDICT__ = {}

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
def test_server_should_start():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = default_context
    server.start()

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

@with_fakes
@with_patched_object(Server, "run_server", custom_run_server)
def test_server_start_should_publish_on_before_and_after_server_start_event():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = default_context

    server.start()

@with_fakes
@with_patched_object(Server, "run_server", custom_run_server)
def test_server_start_calls_run_server():
    clear_expectations()
    server = Server(root_dir="some")
    server.context = default_context

    server.start()

settings_context = Fake('context').has_attr(settings=Fake('settings'))
settings_context.settings.has_attr(Ion=Fake('ion'))
settings_context.settings.Ion.has_attr(host="somehost", port=4728, baseurl="http://some.url:4728", verbose=True)
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
                   'tools.staticdir.root': "some/skink/",
                   'log.screen': True,
                   'tools.sessions.on': True
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
@with_patched_object("skink.lib.cherrypy", "dispatch", custom_dispatch)
def test_get_dispatcher():
    clear()
    server = Server(root_dir="some", context=None)

    dispatcher = server.get_dispatcher()

    assert dispatcher
    assert dispatcher == routes_dispatcher

@with_fakes
@with_patched_object("skink.lib.cherrypy", "dispatch", custom_dispatch)
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

@with_fakes
@with_patched_object("skink.lib.cherrypy", "config", custom_config)
@with_patched_object("skink.lib.cherrypy", "tree", fake_tree)
@with_patched_object(Server, "get_server_settings", fake_get_server_settings)
@with_patched_object(Server, "get_dispatcher", fake_get_dispatcher)
@with_patched_object(Server, "get_mounts", fake_get_mounts)
def test_run_server_updates_config():
    clear()

    server = Server(root_dir="some", context=None)

    server.run_server()

    assert server.app
    assert server.app == "app"

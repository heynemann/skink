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
from skink.lib.ion.controllers import Controller, route

def clear():
    ctrl.__CONTROLLERS__ = []
    ctrl.__CONTROLLERSDICT__ = {}

def test_can_create_controller():
    ctrl = Controller()
    assert ctrl

def test_controller_has_null_context_by_default():
    ctrl = Controller()

    assert not ctrl.context

def test_controller_has_null_server_by_default():
    ctrl = Controller()

    assert not ctrl.server

@with_fakes
def test_controller_has_empty_routes_by_default():
    clear_expectations()
    clear()
    class TestController(Controller):
        pass

    ctrl = TestController()

    assert ctrl.__routes__ is not None
    assert not ctrl.__routes__
    assert isinstance(ctrl.__routes__, list)

@with_fakes
def test_all_controllers_returns_all_imported_controllers():
    clear_expectations()
    clear()
    class TestController2(Controller):
        pass

    controllers = Controller.all()

    assert controllers
    assert len(controllers) == 1
    assert controllers[0] == TestController2

@with_fakes
def test_route_decorator_registers_route_information():
    clear_expectations()
    clear()
    class TestController(Controller):
        @route("/something")
        def SomeAction(self):
            pass

    assert TestController.__routes__

    #Example of a route
    #('SomeAction', {'route': '/something', 'method': 'SomeAction'})
    assert TestController.__routes__[0][0] == 'SomeAction'
    assert TestController.__routes__[0][1]['route'] == '/something'
    assert TestController.__routes__[0][1]['method'] == 'SomeAction'

@with_fakes
def test_route_decorator_registers_route_with_custom_name():
    clear_expectations()
    clear()
    class TestController(Controller):
        @route("/something", name="named_route")
        def SomeAction(self):
            pass

    assert TestController.__routes__

    assert TestController.__routes__[0][0] == 'named_route'
    assert TestController.__routes__[0][1]['route'] == '/something'
    assert TestController.__routes__[0][1]['method'] == 'SomeAction'

dispatcher = Fake("dispatcher")
dispatcher.expects("connect").with_args("test_SomeAction", "/something", controller=arg.any_value(), action="SomeAction")
@with_fakes
def test_register_routes():
    clear_expectations()
    clear()

    class TestController(Controller):
        @route("/something")
        def SomeAction(self):
            pass

    ctrl = TestController()

    ctrl.register_routes(dispatcher)

template_context = Fake('context').has_attr(settings=Fake('settings'))
template_context.settings.has_attr(Ion=Fake('ion'))
template_context.settings.Ion.has_attr(template_path="some/path/to/templates")

template_loader = Fake('template_loader')
environment = Fake(callable=True).with_args(loader=arg.any_value()).returns(template_loader)
package_loader = Fake(callable=True).with_args(arg.endswith("some/root/some/path/to/templates"))

template_fake = Fake('template')
template_loader.expects('get_template').with_args('some_file.html').returns(template_fake)
template_fake.expects('render').with_args(some="args").returns("expected")

@with_fakes
@with_patched_object(ctrl, "Environment", environment)
@with_patched_object(ctrl, "FileSystemLoader", package_loader)
def test_render_template():
    clear_expectations()
    clear()

    ctrl = Controller()
    ctrl.server = Fake('server')
    ctrl.server.has_attr(root_dir="some/root")
    ctrl.context = template_context
    content = ctrl.render_template("some_file.html", some="args")

    assert content == "expected"

template_context2 = Fake('context').has_attr(settings=Fake('settings'))
template_context2.settings.has_attr(Ion=Fake('ion'))
template_context2.settings.Ion.has_attr(template_path="/templates")

simpler_package_loader = Fake(callable=True).with_args(arg.endswith("some/root/templates"))

@with_fakes
@with_patched_object(ctrl, "Environment", environment)
@with_patched_object(ctrl, "FileSystemLoader", simpler_package_loader)
def test_render_template_in_folder_without_package():
    clear_expectations()
    clear()

    ctrl = Controller()
    ctrl.server = Fake('server')
    ctrl.server.has_attr(root_dir="some/root")
    ctrl.context = template_context2

    content = ctrl.render_template("some_file.html", some="args")

    assert content == "expected"

template_context3 = Fake('context').has_attr(settings=Fake('settings'))
template_context3.settings.has_attr(Ion=Fake('ion'))
template_context3.settings.Ion.has_attr(template_path="")

empty_package_loader = Fake(callable=True).with_args(arg.endswith('some/root/templates'))

@with_fakes
@with_patched_object(ctrl, "Environment", environment)
@with_patched_object(ctrl, "FileSystemLoader", empty_package_loader)
def test_render_template_in_folder_with_null_package():
    clear_expectations()
    clear()

    ctrl = Controller()
    ctrl.server = Fake('server')
    ctrl.server.has_attr(root_dir="some/root")
    ctrl.context = template_context3
    content = ctrl.render_template("some_file.html", some="args")

    assert content == "expected"

fake_thread_data = Fake('thread_data')
fake_thread_data.has_attr(store="store")

@with_fakes
@with_patched_object(ctrl, "thread_data", fake_thread_data)
def test_controller_returns_store_from_cherrypy_thread_data():
    clear_expectations()
    clear()

    ctrl = Controller()
    assert ctrl.store == "store"


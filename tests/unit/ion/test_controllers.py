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

def test_controller_has_empty_routes_by_default():
    clear()
    class TestController(Controller):
        pass

    ctrl = TestController()

    assert ctrl.__routes__ is not None
    assert not ctrl.__routes__
    assert isinstance(ctrl.__routes__, list)

def test_all_controllers_returns_all_imported_controllers():
    clear()
    class TestController2(Controller):
        pass

    controllers = Controller.all()

    assert controllers
    assert len(controllers) == 1
    assert controllers[0] == TestController2

def test_route_decorator_registers_route_information():
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

def test_route_decorator_registers_route_with_custom_name():
    clear()
    class TestController(Controller):
        @route("/something", name="named_route")
        def SomeAction(self):
            pass

    assert TestController.__routes__

    assert TestController.__routes__[0][0] == 'named_route'
    assert TestController.__routes__[0][1]['route'] == '/something'
    assert TestController.__routes__[0][1]['method'] == 'SomeAction'


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

import skink.src.controllers.controllers as controllers

import skink.lib
import ion.controllers as ctrl

from skink.src.models import *

def clear():
    ctrl.__CONTROLLERS__ = []
    ctrl.__CONTROLLERSDICT__ = {}

fake_store = Fake("store")

custom_render_template = Fake(callable=True).with_args('index.html', projects=[0, 1, 2]).returns('Some Result')

@with_patched_object(controllers.IndexController, "render_template", custom_render_template)
@with_patched_object(controllers.IndexController, "store", fake_store)
@with_fakes
def test_index_action():
    clear()
    clear_expectations()

    controllers.IndexController.store.expects('query').with_args(Project).returns(controllers.IndexController.store)
    controllers.IndexController.store.expects("all").returns([0, 1, 2])

    controller = controllers.IndexController()
    result = controller.index()

    assert result == "Some Result"

new_render_template = Fake(callable=True).with_args('add_project.html').returns('Create Project')

@with_patched_object(controllers.ProjectController, "render_template", new_render_template)
@with_fakes
def test_new_action():
    clear()
    clear_expectations()

    controller = controllers.ProjectController()
    result = controller.new()

    assert result == "Create Project"


store_create_action = Fake('store')
redirect_create_action = Fake(callable=True).with_args("/")

@with_patched_object(controllers.ProjectController, "store", store_create_action)
@with_patched_object(controllers.ProjectController, "redirect", redirect_create_action)
@with_fakes
def test_create_action():
    clear()
    clear_expectations()

    store_create_action.expects('add').with_args(arg.any_value())

    controller = controllers.ProjectController()

    controller.create(name=u"project_name", build_script=u"build_script", scm_repository=u"scm_repository", monitor_changes="MONITOR", branch="master")


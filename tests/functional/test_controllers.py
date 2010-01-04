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

from os.path import abspath, join, dirname

import skink.lib
import ion.controllers as ctrl
from ion import Server, ServerStatus, Context
from ion.controllers import Controller, route

from base import *
from skink.src.controllers import *
from skink.src.models import Project

store = create_store()
create_models(store)
Controller.store = store

root_dir = abspath(join(dirname(__file__), "../../"))

def test_index_controller_index_action():
    server = Server(root_dir)

    server.start('config.ini', non_block=True)

    while not server.status == ServerStatus.Started:
        time.sleep(0.5)

    controller = IndexController()
    controller.server = server
    controller.context = server.context

    content = controller.index()

    assert content

def test_index_controller_index_action_with_created_projects():
    proj = Project(name=u"Index Test Project 2", build_script=u"test build script", scm_repository=u"scm_repository", monitor_changes=False)

    store.add(proj)

    store.commit()

    server = Server(root_dir)

    server.start('config.ini', non_block=True)

    while not server.status == ServerStatus.Started:
        time.sleep(0.5)

    controller = IndexController()
    controller.server = server
    controller.context = server.context

    content = controller.index()

    assert content

def test_project_controller_new_action():
    server = Server(root_dir)

    server.start('config.ini', non_block=True)

    while not server.status == ServerStatus.Started:
        time.sleep(0.5)

    controller = ProjectController()
    controller.server = server
    controller.context = server.context

    content = controller.new()

    assert content

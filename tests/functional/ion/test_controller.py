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
import time

import skink.lib
import ion.controllers as ctrl
from ion import Server, ServerStatus, Context
from ion.controllers import Controller, route

root_dir = abspath(dirname(__file__))

def clear():
    ctrl.__CONTROLLERS__ = []
    ctrl.__CONTROLLERSDICT__ = {}

def test_can_render_template_from_null_template_folder():
    clear()

    class TemplateFolderController(Controller):
        pass

    server = Server(root_dir)

    server.start('controller_config1.ini', non_block=True)

    while not server.status == ServerStatus.Started:
        time.sleep(0.5)

    controller = TemplateFolderController()
    controller.server = server
    controller.context = server.context
    content = controller.render_template('test_template.html')
    
    assert content == "Hello World"

def test_can_render_template_from_specific_template_folder():
    clear()

    class TemplateFolderController(Controller):
        pass

    server = Server(root_dir)

    server.start('controller_config2.ini', non_block=True)

    while not server.status == ServerStatus.Started:
        time.sleep(0.5)

    controller = TemplateFolderController()
    controller.server = server
    controller.context = server.context
    content = controller.render_template('test_template.html')
    
    assert content == "Hello World 2"

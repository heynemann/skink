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

from os.path import abspath, dirname, join

import skink.lib
import ion.controllers as ctrl
from ion import Server, ServerStatus, Context
from ion.controllers import Controller, route

from client import HttpClient

def clear():
    ctrl.__CONTROLLERS__ = []
    ctrl.__CONTROLLERSDICT__ = {}

root_dir = abspath(dirname(__file__))
config_path = 'config.ini'

def test_server_can_start():
    clear()
    server = Server(root_dir=root_dir)
    try:
        server.start(config_path=config_path, non_block=True)

        assert server.status == ServerStatus.Started
    finally:
        server.stop()

def test_server_responds_for_controller_action():
    clear()

    class TestController(Controller):
        @route("/")
        def SomeAction(self):
            return "Hello World"

    server = Server(root_dir=root_dir)

    try:
        server.start(config_path=config_path, non_block=True)

        status_code, content = HttpClient.get(server.context.settings.Ion.baseurl)

        assert status_code == 200
        assert content == "Hello World"
    finally:
        server.stop()



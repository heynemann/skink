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

from skink.infra import Server, ServerStatus, Context

def test_server_status_statuses():
    assert ServerStatus.Unknown == 0
    assert ServerStatus.Starting == 1
    assert ServerStatus.Started == 2
    assert ServerStatus.Stopping == 3
    assert ServerStatus.Stopped == 4

def test_server_should_have_unknown_status_by_default():
    server = Server()
    assert server.status == ServerStatus.Unknown

def test_server_should_start():
    server = Server()
    server.start()

    assert server.status == ServerStatus.Started

def test_server_should_have_context():
    server = Server()

    assert server.context

def test_server_should_have_context_of_type_context():
    server = Server()

    assert isinstance(server.context, Context)

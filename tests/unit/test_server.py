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

from fudge import Fake, with_fakes, with_patched_object
from fudge.inspector import arg
from fudge_extensions import clear

from skink.lib.ion import Server, ServerStatus, Context

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

@with_fakes
@with_patched_object(Server, "run_server", custom_run_server)
@clear
def test_server_should_start():
    server = Server(root_dir="some")
    server.context = default_context
    server.start()

    assert server.status == ServerStatus.Started

def test_server_should_have_context():
    server = Server(root_dir="some")

    assert server.context

def test_server_should_have_context_of_type_context():
    server = Server(root_dir="some")

    assert isinstance(server.context, Context)

context = Fake('context').has_attr(bus=Fake('bus'))
context.bus.expects('subscribe').with_args("anything", arg.any_value())

@with_fakes
@with_patched_object(Server, "run_server", custom_run_server)
@clear
def test_server_subscribe_calls_bus_subscribe():
    server = Server(root_dir="some")
    server.context = context

    server.subscribe('anything', lambda server, bus, arguments: None)

default_context = Fake('context').has_attr(bus=Fake('bus'))
default_context.bus.expects('publish').with_args("on_before_server_start", arg.any_value())
default_context.bus.next_call(for_method='publish').with_args("on_after_server_start", arg.any_value())

@with_fakes
@with_patched_object(Server, "run_server", custom_run_server)
@clear
def test_server_start_should_publish_on_before_and_after_server_start_event():
    server = Server(root_dir="some")
    server.context = default_context

    server.start()

@with_fakes
@with_patched_object(Server, "run_server", custom_run_server)
@clear
def test_server_start_calls_run_server():
    server = Server(root_dir="some")
    server.context = default_context

    server.start()


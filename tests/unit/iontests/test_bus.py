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

from skink.lib.ion import Bus

def test_can_create_bus():
    bus = Bus()
    assert bus

def test_can_subscribe_to_a_message():
    bus = Bus()
    
    bus.subscribe('some_message', lambda: None)
    
    assert len(bus.subscriptions) == 1

def test_can_publish_a_message_with_no_subscribers():
    bus = Bus()
    
    bus.publish('some_message', {})
    
    #should just work

called_1 = False
called_2 = False
def test_subscribers_get_called_on_publish():
    bus = Bus()
    
    def on_1(data):
        global called_1
        called_1 = True

    def on_2(data):
        global called_2
        called_2 = True
    
    bus.subscribe('some_message', on_1)
    bus.subscribe('some_message', on_2)
    
    bus.publish('some_message', {})
    
    assert called_1
    assert called_2


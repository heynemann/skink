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

from skink.infra.context import Context

class ServerStatus(object):
    Unknown = 0
    Starting = 1
    Started = 2
    Stopping = 3
    Stopped = 4

class Server(object):
    def __init__(self):
        self.status = ServerStatus.Unknown
        self.context = Context()

    def start(self):
        #self.context.bus.publish('on_before_server_start', {'self':self, 'context':self.context})
        self.status = ServerStatus.Starting

        self.status = ServerStatus.Started

    def subscribe(self, subject, handler):
        self.context.bus.subscribe(subject, handler)


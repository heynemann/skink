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

class Bus(object):
    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, subject, func):
        if not subject in self.subscriptions:
            self.subscriptions[subject] = []
        self.subscriptions[subject].append(func)

    def publish(self, subject, data, *args, **kw):
        if subject not in self.subscriptions:
            return

        for subscription in self.subscriptions[subject]:
            subscription(data, *args, **kw)

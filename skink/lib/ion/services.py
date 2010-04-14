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

import cherrypy
from ion.db import Db

class Service(object):
    def __init__(self, server):
        self.server = server
        self.db = None
        self.store = None

    def log(self, message):
        if self.server.context.settings.Ion.as_bool('verbose'):
            cherrypy.log(message, "[%s]" % self.__class__.__name__)

    def connect(self):
        db = Db(self.server)
        db.connect()
        self.db = db
        self.store = db.store

    def disconnect(self):
        self.db.disconnect()
        self.db = None
        self.store = None

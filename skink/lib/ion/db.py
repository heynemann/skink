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

from storm.locals import *

class Db(object):
    def __init__(self, context):
        self.is_connected = False
        self.context = context
        self.store = None

    def connect(self):
        if self.is_connected:
            raise RuntimeError("You have to disconnect before connecting again")
        self.is_connected = True

        database = create_database(self.connstr)
        self.store = Store(database)

    def disconnect(self):
        if not self.is_connected:
            raise RuntimeError("You have to connect before disconnecting")

        self.store.close()
        self.store = None
        self.is_connected = False

    @property
    def connstr(self):
        protocol = self.context.settings.Db.protocol
        username = self.context.settings.Db.user
        password = self.context.settings.Db.password
        host = self.context.settings.Db.host
        port = int(self.context.settings.Db.port)
        database = self.context.settings.Db.database

        return "%s://%s:%s@%s:%d/%s" % (
            protocol,
            username,
            password,
            host,
            port,
            database
        )

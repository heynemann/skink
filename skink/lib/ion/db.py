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

from sqlalchemy import MetaData, create_engine, __version__ as sa_version
from sqlalchemy.orm import scoped_session, sessionmaker

if sa_version.split(".") < ["0", "5", "0"]:
    raise ImportError("Version 0.5 or later of SQLAlchemy required.")

def new_session():
    return scoped_session(sessionmaker(autoflush=True, autocommit=False))

metadata = MetaData()
session = new_session()
mapper = session.mapper

class Db(object):
    def __init__(self, server):
        self.is_connected = False
        self.server = server
        self.store = None

    def connect(self):
        if self.is_connected:
            raise RuntimeError("You have to disconnect before connecting again")
        self.is_connected = True

        engine = create_engine(self.connstr, echo=False, convert_unicode=True)
        session.bind = engine

        self.store = session

    def disconnect(self):
        if not self.is_connected:
            raise RuntimeError("You have to connect before disconnecting")

        self.store.close()
        self.store = None
        self.is_connected = False

    @property
    def connstr(self):
        protocol = self.server.context.settings.Db.protocol
        username = self.server.context.settings.Db.user
        password = self.server.context.settings.Db.password
        host = self.server.context.settings.Db.host
        port = int(self.server.context.settings.Db.port)
        database = self.server.context.settings.Db.database

        return "%s://%s:%s@%s:%d/%s" % (
            protocol,
            username,
            password,
            host,
            port,
            database
        )

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

import time
from threading import Thread

import cherrypy
from cherrypy.process import plugins
from ion.db import Db

class CherryPyPlugin(plugins.SimplePlugin):
    #it's called do_log due to cherrypy having a log method already
    def do_log(self, message):
        if self.server.context.settings.Ion.as_bool("verbose"):
            cherrypy.log(message, "[%s]" % self.key)

    def __init__(self, bus, server):
        if not hasattr(self, 'key'):
            raise ValueError('The plugin does not have a key. Please make sure that you have a class variable named "key" that uniquely identifies this plugin')
        super(CherryPyPlugin, self).__init__(bus)
        self.server = server

class CherryPyDaemonPlugin(CherryPyPlugin):
    def __init__(self, bus, server):
        super(CherryPyDaemonPlugin, self).__init__(bus, server)
        self.should_die = False
        self.thread = None
        self.store = None

    def start(self):
        self.thread = Thread(target=self.loop_execute)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        self.do_log("Killing monitor...")
        self.should_die = True
        self.do_log("Monitor dead.")

    def loop_execute(self):
        ctx = self.server.context
        while(not self.should_die):
            db = Db(self.server)
            try:
                db.connect()
                self.store = db.store

                self.execute()
            except Exception:
                cherrypy.engine.exit()
                raise
            finally:
                db.disconnect()
                self.store = None

    def execute(self):
        pass

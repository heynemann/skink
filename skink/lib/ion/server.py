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

from os.path import join, abspath, dirname

#this import is required in order to include the lib folder in pythonpath
import skink.lib

import cherrypy
from ion.controllers import Controller

from context import Context

class ServerStatus(object):
    Unknown = 0
    Starting = 1
    Started = 2
    Stopping = 3
    Stopped = 4

class Server(object):
    def __init__(self, root_dir, context=None):
        self.status = ServerStatus.Unknown
        self.root_dir = root_dir
        self.context = context or Context(root_dir=root_dir)

    def start(self, config_path, non_block=False):
        self.status = ServerStatus.Starting
        self.publish('on_before_server_start', {'server':self, 'context':self.context})

        self.context.load_settings(abspath(join(self.root_dir, config_path)))

        self.run_server(non_block)

        self.status = ServerStatus.Started
        self.publish('on_after_server_start', {'server':self, 'context':self.context})

    def stop(self):
        self.status = ServerStatus.Stopping
        self.publish('on_before_server_stop', {'server':self, 'context':self.context})

        cherrypy.engine.exit()

        self.status = ServerStatus.Stopped
        self.publish('on_after_server_stop', {'server':self, 'context':self.context})

    def get_server_settings(self):
        sets = self.context.settings
        return {
                   'server.socket_host': sets.Ion.host,
                   'server.socket_port': int(sets.Ion.port),
                   'request.base': sets.Ion.baseurl,
                   'tools.encode.on': True, 
                   'tools.encode.encoding': 'utf-8',
                   'tools.decode.on': True,
                   'tools.trailing_slash.on': True,
                   'tools.staticdir.root': join(self.root_dir, "skink/"),
                   'log.screen': sets.Ion.verbose == "True",
                   'tools.sessions.on': True
               }

    def get_mounts(self, dispatcher):
        conf = {
            '/': {
                'request.dispatch': dispatcher,
            },
            '/media': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'media'
            }
        }

        return conf

    def get_dispatcher(self):
        routes_dispatcher = cherrypy.dispatch.RoutesDispatcher()

        for controller_type in Controller.all():
            controller = controller_type()
            controller.server = self
            controller.context = self.context
            controller.register_routes(routes_dispatcher)

        dispatcher = routes_dispatcher
        return dispatcher

    def run_server(self, non_block=False):
        cherrypy.config.update(self.get_server_settings())
        dispatcher = self.get_dispatcher()
        mounts = self.get_mounts(dispatcher)

        self.app = cherrypy.tree.mount(None, config=mounts)
        
        cherrypy.engine.start()
        if not non_block:
            cherrypy.engine.block()

    def subscribe(self, subject, handler):
        self.context.bus.subscribe(subject, handler)

    def publish(self, subject, data):
        self.context.bus.publish(subject, data)


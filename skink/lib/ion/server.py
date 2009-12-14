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

from context import Context

class ServerStatus(object):
    Unknown = 0
    Starting = 1
    Started = 2
    Stopping = 3
    Stopped = 4

class Server(object):
    def __init__(self, root_dir):
        self.status = ServerStatus.Unknown
        self.root_dir = root_dir
        self.context = Context(root_dir=root_dir)

    def start(self):
        self.publish('on_before_server_start', {'server':self, 'context':self.context})
        self.status = ServerStatus.Starting

        self.run_server()

        self.status = ServerStatus.Started
        self.publish('on_after_server_start', {'server':self, 'context':self.context})

    def run_server(self):
        pass
#        cherrypy.config.update({
#                'server.socket_host': ctx.host,
#                'server.socket_port': ctx.port,
#                'request.base': ctx.root,
#                'tools.encode.on': True, 
#                'tools.encode.encoding': 'utf-8',
#                'tools.decode.on': True,
#                'tools.trailing_slash.on': True,
#                'tools.staticdir.root': join(self.root_dir, "skink/"),
#                'tools.ElixirTransaction.on': True,
#                'log.screen': ctx.webserver_verbose,
#                'tools.sessions.on': True
#            })

#        conf = {
#            '/': {
#                'request.dispatch': cls.__setup_routes(),
#            },
#            '/media': {
#                'tools.staticdir.on': True,
#                'tools.staticdir.dir': 'media'
#            }
#        }

#        app = cherrypy.tree.mount(None, config=conf)

    def subscribe(self, subject, handler):
        self.context.bus.subscribe(subject, handler)

    def publish(self, subject, data):
        self.context.bus.publish(subject, data)


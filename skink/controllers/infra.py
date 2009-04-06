#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

import cherrypy
from elixir import *

from skink.controllers import IndexController

class Server(object):
    @classmethod
    def start(self):
        Db.verify_and_create()
        cherrypy.config.update({
            'server.socket_host':'0.0.0.0',
            'server.socket_port': 8088,
            'tools.encode.on': True, 'tools.encode.encoding': 'utf-8',
            'tools.decode.on': True,
            'tools.trailing_slash.on': True,
            'tools.staticdir.root': join(root_path, "skink/"),
        })
        cherrypy.quickstart(IndexController(), '/', {
            '/media': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'media'
            }
        })

    @classmethod
    def stop(self):
        cherrypy.engine.stop()

class Db(object):
    @classmethod
    def verify_and_create(self):
        metadata.bind = 'sqlite:///skinkdb.db'
        setup_all()
        if not exists("skink.db"):
            create_all()

if __name__ == '__main__':
    Server.start()

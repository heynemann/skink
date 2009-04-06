#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

import cherrypy

import template

class IndexController(object):
    @cherrypy.expose
    @template.output("index.html")
    def index(self):
        return template.render()

class Server(object):
    @classmethod
    def start(self):
        cherrypy.config.update({
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

if __name__ == '__main__':
    Server.start()

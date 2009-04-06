#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

import cherrypy
from elixir import *

from skink.models import metadata, setup_all, drop_all
from skink.repositories import ProjectRepository
import template

class ProjectController(object):
    @cherrypy.expose
    @template.output("create_project.html")
    def new(self):
        return template.render()

    @cherrypy.expose
    def create(self, name, build_script):
        repository = ProjectRepository()
        project = repository.create(name=name, build_script=build_script)
        raise cherrypy.HTTPRedirect('/')

class IndexController(object):
    project = ProjectController()
    
    @cherrypy.expose
    @template.output("index.html")
    def index(self):
        repository = ProjectRepository()
        projects = repository.get_all()
        return template.render(projects=projects)

class Server(object):
    @classmethod
    def start(self):
        Db.verify_and_create()
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

class Db(object):
    @classmethod
    def verify_and_create(self):
        metadata.bind = 'sqlite:///skinkdb.db'
        setup_all()
        if not exists("skink.db"):
            create_all()

if __name__ == '__main__':
    Server.start()

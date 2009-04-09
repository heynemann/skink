#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.imports import *
from skink.models import *
from skink.controllers import IndexController, ProjectController
from skink.context import SkinkContext

class Server(object):
    @classmethod
    def __setup_routes(cls):
        d = cherrypy.dispatch.RoutesDispatcher()
        d.connect('project_new', 'project/new', controller=ProjectController(), action='new')
        d.connect('project_create', 'project/create', controller=ProjectController(), action='create')
        d.connect('project_edit', 'project/:project_id/edit', controller=ProjectController(), action='edit')
        d.connect('project_update', 'project/:project_id/update', controller=ProjectController(), action='update')
        d.connect('project_delete', 'project/:project_id/delete', controller=ProjectController(), action='delete')
        d.connect('project_build', 'project/:project_id/build', controller=ProjectController(), action='build')
        d.connect('project_details', 'project/:project_id', controller=ProjectController(), action='details')
        d.connect('build_details', 'project/:project_id/builds/:build_id', controller=ProjectController(), action='build_details')
        d.connect('index', ':action', controller=IndexController())
        dispatcher = d
        return dispatcher

    @classmethod
    def start(cls):
        Db.verify_and_create()

        cherrypy.config.update({
            'server.socket_host':SkinkContext.current().host,
            'server.socket_port': SkinkContext.current().port,
            'tools.encode.on': True, 'tools.encode.encoding': 'utf-8',
            'tools.decode.on': True,
            'tools.trailing_slash.on': True,
            'tools.staticdir.root': join(root_path, "skink/")
            })

        conf = {
            '/': {
                'request.dispatch': cls.__setup_routes(),
            },
            '/media': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'media'
            }
        }

        app = cherrypy.tree.mount(None, config=conf)
        cherrypy.quickstart(app)

    @classmethod
    def stop(self):
        cherrypy.engine.stop()

class Db(object):
    @classmethod
    def verify_and_create(self):
        metadata.bind = 'sqlite:///skinkdb.db'
        metadata.bind.echo = True
        setup_all()
        if not exists("skinkdb.db"):
            create_all()

if __name__ == '__main__':
    Server.start()

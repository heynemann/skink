#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import os
import time
import thread

from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.imports import *
from skink.models import *
from skink.controllers import IndexController, ProjectController, PipelineController
from skink.controllers.elixir_tool import ElixirTransaction
from skink.context import SkinkContext
from skink.repositories import ProjectRepository
from skink.services import BuildService
from skink.services.scm import GitRepository
from skink.plugins import PluginEvents
from builder import BuilderPlugin
from monitor import MonitorPlugin

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
        d.connect('project_build_status', 'buildstatus', controller=ProjectController(), action='build_status')
        d.connect('pipeline_index', 'pipeline', controller=PipelineController(), action='index')
        d.connect('create_pipeline', 'pipeline/create', controller=PipelineController(), action='create')
        d.connect('edit_pipeline', 'pipeline/:pipeline_id', controller=PipelineController(), action='edit')
        d.connect('update_pipeline', 'pipeline/:pipeline_id/update', controller=PipelineController(), action='update')
        d.connect('delete_pipeline', 'pipeline/:pipeline_id/delete', controller=PipelineController(), action='delete')

        d.connect('status', 'status', controller=ProjectController(), action='get_all_status')

        d.connect('login', 'login', controller=IndexController(), action='login')
        d.connect('login_error', 'loginerror', controller=IndexController(), action='login_error')
        d.connect('logoff', 'logoff', controller=IndexController(), action='logoff')

        d.connect('index', ':action', controller=IndexController())
        dispatcher = d
        return dispatcher

    @classmethod
    def start(cls):
        ctx = SkinkContext.current()
        Db.verify_and_create()

        cherrypy.config.update({
                'server.socket_host': ctx.host,
                'server.socket_port': ctx.port,
                'request.base': ctx.root,
                'tools.encode.on': True, 
                'tools.encode.encoding': 'utf-8',
                'tools.decode.on': True,
                'tools.trailing_slash.on': True,
                'tools.staticdir.root': join(root_path, "skink/"),
                'tools.ElixirTransaction.on': True,
                'log.screen': ctx.webserver_verbose,
                'tools.sessions.on': True
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
        
        #starting cherrypy plugins
        build_path = join(root_path, SkinkContext.current().build_path)
        builder_plugin = BuilderPlugin(cherrypy.engine, BuildService())
        monitor_plugin = MonitorPlugin(cherrypy.engine, ProjectRepository(), GitRepository(build_path))

        builder_plugin.subscribe()
        monitor_plugin.subscribe()

        cherrypy.quickstart(app)

    @classmethod
    def stop(cls):
        print "Killing skink..."
        cherrypy.engine.exit()
        print "skink killed."

class Db(object):
    @classmethod
    def verify_and_create(cls):
        ctx = SkinkContext.current()
        metadata.bind = ctx.db_connection
        metadata.bind.echo = ctx.db_verbose
        setup_all()
        
        if not cls.is_db_created():
            create_all()

    @classmethod
    def is_db_created(cls):
        rep = ProjectRepository()
        try:
            projects = rep.get_all()
        except Exception, err:
            return False
        return True

if __name__ == '__main__':
    Server.start()

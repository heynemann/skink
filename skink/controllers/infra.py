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
from skink.context import SkinkContext
from skink.repositories import ProjectRepository
from skink.services import BuildService
from skink.services.scm import GitRepository
from skink.plugins import PluginEvents

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

        d.connect('login', 'login', controller=IndexController(), action='login')
        d.connect('login_error', 'loginerror', controller=IndexController(), action='login_error')
        d.connect('logoff', 'logoff', controller=IndexController(), action='logoff')

        d.connect('index', ':action', controller=IndexController())
        dispatcher = d
        return dispatcher

    @classmethod
    def start(cls):
        try:
            ctx = SkinkContext.current()
            Db.verify_and_create()
            
            cls.builders = []
            for i in range(ctx.worker_processes):
                builder = Builder(BuildService())
                cls.builders.append(builder)
                builder.start()
            
            build_path = join(root_path, SkinkContext.current().build_path)
            monitor = Monitor(ProjectRepository(), GitRepository(build_path))
            cls.monitor = monitor
            monitor.start()

            cherrypy.config.update({
                    'server.socket_host': ctx.host,
                    'server.socket_port': ctx.port,
                    'tools.encode.on': True, 'tools.encode.encoding': 'utf-8',
                    'tools.decode.on': True,
                    'tools.trailing_slash.on': True,
                    'tools.staticdir.root': join(root_path, "skink/"),
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
            cherrypy.quickstart(app)
        finally:
            cls.stop()

    @classmethod
    def stop(cls):
        print "Killing skink..."
        for builder in cls.builders:
            builder.stop()
        cls.monitor.stop()
        cherrypy.engine.exit()
        print "skink killed."

class Builder(object):
    def __init__(self, build_service):
        self.build_service = build_service
        self.should_die = False
        
    def start(self):
        thread.start_new_thread(self.process_build_queue, tuple([]))

    def stop(self):
        print "Killing builder..."
        self.should_die = True
        print "Builder dead."

    def process_build_queue(self):
        ctx = SkinkContext.current()
        while(not self.should_die):
            if ctx.build_verbose:
                print "Polling Queue for projects to build..."
            if ctx.build_queue:
                item = ctx.build_queue.pop()
                if ctx.build_verbose:
                    print "Found %s to build. Building..." % item
                self.build_service.build_project(item)
            time.sleep(ctx.build_polling_interval)
            
class Monitor(object):
    def __init__(self, project_repository, scm):
        self.project_repository = project_repository
        self.scm = scm
        self.should_die = False
        
    def start(self):
        thread.start_new_thread(self.process_monitored_projects, tuple([]))
        
    def stop(self):
        print "Killing monitor..."
        self.should_die = True
        print "Monitor dead."

    def process_monitored_projects(self):
        ctx = SkinkContext.current()

        while(not self.should_die):
            monitored_projects = self.project_repository.get_projects_to_monitor()
            if not monitored_projects and ctx.scm_verbose:
                print "No projects found for monitoring..."
            for project in monitored_projects:
                if project.id in ctx.projects_being_built:
                    continue
                if ctx.scm_verbose:
                    print "Polling %s..." % project.name
                if self.scm.does_project_need_update(project):
                    if ctx.scm_verbose:
                        print "Adding project %s(%d) to the queue due to remote changes." % (project.name, project.id)
                    ctx.build_queue.append(project.id)
                else:
                    if ctx.scm_verbose:
                        print "Project %s is already up-to-date" % project.name
                time.sleep(2)
            time.sleep(ctx.polling_interval)

class Db(object):
    @classmethod
    def verify_and_create(cls):
        ctx = SkinkContext.current()
        metadata.bind = ctx.db_connection
        metadata.bind.echo = ctx.db_verbose
        setup_all()
        if not exists("skinkdb.db"):
            create_all()

if __name__ == '__main__':
    Server.start()

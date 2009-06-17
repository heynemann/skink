#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import time
from threading import Thread

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

class MonitorPlugin(plugins.SimplePlugin):
    def __init__(self, bus, project_repository, scm):
        plugins.SimplePlugin.__init__(self, bus)
        self.project_repository = project_repository
        self.scm = scm
        self.should_die = False
        self.thread = None

    def start(self):
        self.thread = Thread(target = self.process_monitored_projects)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        print "Killing monitor..."
        self.should_die = True
#        try:
#            self.thread.join()
#        except RuntimeError, err:
#            if err.message != "cannot join current thread":
#                raise
        print "Monitor dead."

    def process_monitored_projects(self):
        ctx = SkinkContext.current()

        while(not self.should_die):
            try:
                monitored_projects = self.project_repository.get_projects_to_monitor()
                if not monitored_projects and ctx.scm_verbose:
                    print "No projects found for monitoring..."
                for project in monitored_projects:
                    if project.id in ctx.projects_being_built:
                        continue
                    if project.id in ctx.build_queue:
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
            except Exception:
                cherrypy.engine.exit()
                raise

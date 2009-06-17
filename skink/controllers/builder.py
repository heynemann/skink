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

class BuilderPlugin(plugins.SimplePlugin):
    #it's called do_log due to cherrypy having a log method already
    def do_log(self, message):
        ctx = SkinkContext.current()
        if ctx.build_verbose:
            print message
        
    def __init__(self, bus, build_service):
        plugins.SimplePlugin.__init__(self, bus)
        self.build_service = build_service
        self.should_die = False
        self.thread = None

    def start(self):
        self.thread = Thread(target=self.process_build_queue)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        print "Killing builder..."
        self.should_die = True
        #try:
            #self.thread.join()
        #except RuntimeError, err:
            #if err.message != "cannot join current thread":
                #raise
        print "Builder dead."

    def process_build_queue(self):
        ctx = SkinkContext.current()
        while(not self.should_die):
            try:
                self.do_log("Polling Queue for projects to build...")
                if ctx.build_queue:
                    item = ctx.build_queue.pop()
                    self.do_log("Found %s to build. Building..." % item)
                    self.build_service.build_project(item)
                    self.do_log("Project %s finished building." % item)
                time.sleep(ctx.build_polling_interval)
            except Exception:
                cherrypy.engine.exit()
                raise

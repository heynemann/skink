#!/usr/bin/env python
# -*- coding:utf-8 -*-

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

class BuilderPlugin(plugins.SimplePlugin):
    def __init__(self, bus, build_service):
        plugins.SimplePlugin.__init__(self, bus)
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
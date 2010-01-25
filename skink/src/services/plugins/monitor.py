#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time

import skink.lib
from cherrypy import thread_data
from ion.plugins import CherryPyDaemonPlugin

from skink.src.models import *
from skink.src.services.scm import GitService

class MonitorPlugin(CherryPyDaemonPlugin):
    key = "MONITOR"

    def execute(self):
        ctx = self.server.context

        self.server.connect_db("MONITORPLUGIN")

        try:
            store = thread_data.store

            monitored_projects = projects = list(store.find(Project, Project.monitor_changes == True))
        finally:
            self.server.disconnect_db("MONITORPLUGIN", do_log=False)

        git_service = GitService(server=self.server)

        if not monitored_projects:
            self.do_log("No projects found for monitoring...")
        else:
            for project in monitored_projects:
                if project.id in ctx.projects_being_built:
                    continue
                if project.id in ctx.build_queue:
                    continue

                self.do_log("Polling %s..." % project.name)

                if git_service.does_project_need_update(project):
                    self.do_log("Adding project %s(%d) to the queue due to remote changes." % (project.name, project.id))
                    ctx.build_queue.append(project.id)
                else:
                    self.do_log("Project %s is already up-to-date" % project.name)
                time.sleep(2)

        time.sleep(int(ctx.settings.Skink.scm_polling_interval))


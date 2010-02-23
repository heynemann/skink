#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright Bernardo Heynemann <heynemann@gmail.com>

# Licensed under the Open Software License ("OSL") v. 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.opensource.org/licenses/osl-3.0.php

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import time
import sys
import glob
from os.path import dirname, abspath, join, exists, split

import skink.lib
from cherrypy import thread_data
from ion.services import Service

from skink.src.models import *
from skink.src.services.scm import *
from skink.src.common import *
from skink.src.services.executers import ShellExecuter

class BuildService(Service):
    Unknown = "Unknown"
    Success = "Successful"
    Failure = "Failed"

    def __init__(self, server):
        self.server = server
        self.base_path = server.build_dir
        self.executer = ShellExecuter(verbose=self.server.context.settings.Ion.as_bool("verbose"))

    def start_execute(self, executer):
        ctx = self.server.context
        ctx.current_command = executer.command
        ctx.current_process = executer
        ctx.current_start_time = time.time()
        ctx.current_project = self.current_project
        ctx.current_log = None

    def execute_beat(self, executer):
        ctx = self.server.context
        ctx.current_command = executer.command
        ctx.current_log = executer.result.log

    def finish_execute(self, executer):
        ctx = self.server.context
        ctx.current_command = None
        ctx.current_start_time = None
        ctx.current_project = None
        ctx.current_log = None

    def build_project(self, project_id):
        ctx = self.server.context

        self.connect()

        try:
            store = self.store
            log = ["Build started at %s" % datetime.now()]

            status = BuildService.Failure
            scm_status = ScmResult.Failed
            project = store.query(Project).get(project_id)

            self.current_project = project

            self.server.publish('on_before_build', {"server":self.server, "project":project})

            ctx.projects_being_built.append(project_id)

            last_build_number = store.query(Build.number).filter(Build.project==project).order_by(desc(Build.id)).first()
            last_build_number = last_build_number and last_build_number[0] or 0

            build_date = datetime.now()
            build_scm_status = scm_status
            build_log = ""

            scm_service = GitService(self.server)

            scm_creation_result = scm_service.create_or_update(project)
            build_scm_status = scm_creation_result.status
            store.commit()

            if scm_creation_result.status == ScmResult.Failed:
                log.append(scm_creation_result.log)
                status = BuildService.Failure
            else:
                log.append("Downloaded code from %s (%s)" % (project.scm_repository, scm_creation_result.status))

                self.executer.start_execute = self.start_execute
                self.executer.finish_execute = self.finish_execute
                self.executer.execute_beat = self.execute_beat

                execute_result = self.executer.execute(project.build_script, 
                                                       scm_creation_result.repository_path, 
                                                       timeout=ctx.settings.Skink.as_int("build_timeout"))

                self.executer.start_execute = None
                self.executer.finish_execute = None
                self.executer.execute_beat = None

                log.append("Executed %s" % project.build_script)
                log.append("Exit Code: %s" % execute_result.exit_code)
                log.append("Run Log:")
                log.append(execute_result.run_log)

                status = execute_result.exit_code == 0 and BuildService.Success or BuildService.Failure

            log.append("Build finished at %s" % datetime.now())

            build = Build(last_build_number + 1,
                          build_date,
                          status,
                          build_scm_status,
                          "\n".join(log),
                          force_unicode(scm_creation_result.last_commit["commit_number"]),
                          force_unicode(scm_creation_result.last_commit["author"]),
                          force_unicode(scm_creation_result.last_commit["committer"]),
                          force_unicode(scm_creation_result.last_commit["subject"]),
                          scm_creation_result.last_commit["author_date"],
                          scm_creation_result.last_commit["committer_date"],
                          project)

            store.add(build)
            store.commit()

            ctx.projects_being_built.remove(project_id)

            if (build.status == BuildService.Success):
                self.server.publish('on_build_successful', {"server":self.server, "project":project, "build":build})
                self.process_pipelines_for(project)
            else:
                self.server.publish('on_build_failed', {"server":self.server, "project":project, "build":build})

            return build
        finally:
            self.disconnect()

    def process_pipelines_for(self, project):
        pipelines = self.store.query(Pipeline) \
                              .filter(PipelineItem.project_id == project.id) \
                              .filter(PipelineItem.pipeline_id == Pipeline.id) \
                              .all()
        for pipeline in pipelines:
            pipeline_items = pipeline.items

            for index, pipeline_item in enumerate(pipeline_items):
                if index == len(pipeline_items) - 1:
                    continue

                if pipeline_item.project_id == project.id:
                    self.log("Adding project %d to the queue because it's in the same pipeline as project %s" % (pipeline_items[index+1].project.id, pipeline_item.project.name))
                    self.server.context.build_queue.append(pipeline_items[index+1].project_id)


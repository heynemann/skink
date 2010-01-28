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

import skink.lib
from ion.controllers import Controller, route, authenticated
from skink.src.models import *
import demjson

class IndexController(Controller):

    @route("/")
    def index(self):
        projects = list(self.store.find(Project))
        return self.render_template("index.html", projects=projects)

    @route("/mini")
    def mini(self):
        projects = list(self.store.find(Project))
        return self.render_template("mini.html", projects=projects)

class ProjectController(Controller):

    @route("/project/new")
    def new(self):
        return self.render_template("add_project.html")

    @route("/project/create")
    def create(self, name, build_script, scm_repository, monitor_changes=None):
        prj = Project(name=name, build_script=build_script, scm_repository=scm_repository, monitor_changes=monitor_changes == "MONITOR")
        self.store.add(prj)

        self.redirect("/")

    @route("/project/:id/edit")
    def edit(self, id):
        project_id = int(id)
        prj = self.store.get(Project, project_id)
        return self.render_template("edit_project.html", project=prj)

    @route("/project/:id/update")
    def update(self, id, name, build_script, scm_repository, monitor_changes=None):
        project_id = int(id)
        prj = self.store.get(Project, project_id)

        prj.name = name
        prj.build_script = build_script
        prj.scm_repository = scm_repository
        prj.monitor_changes = monitor_changes == "MONITOR"

        self.redirect("/project/%d" % project_id)

    @route("/project/:id", priority=1)
    def show_details(self, id):
        prj = self.store.get(Project, int(id))

        return self.render_template("project_details.html", project=prj, current_build=prj.last_build)

    @route("/project/:id/builds/:build_id")
    def show_build_details(self, id, build_id):
        prj = self.store.get(Project, int(id))
        build = self.store.get(Build, int(build_id))

        return self.render_template("project_details.html", project=prj, current_build=build)

    @route("/project/:id/build")
    def build(self, id):
        project_id = int(id)
        self.log("Adding project %s to the queue" % project_id)
        self.context.build_queue.append(project_id)
        self.redirect('/project/%s' % project_id)

    @route("/project/:id/delete")
    def delete(self, id):
        project_id = int(id)

        prj = self.store.get(Project, project_id)

        pipelines = self.store.find(Pipeline,
                                    PipelineItem.pipeline_id == Pipeline.id,
                                    PipelineItem.project_id == project_id)

        for pipeline in pipelines:
            self.store.remove(pipeline)

        self.store.remove(prj)

        self.redirect('/')

    @route("project/:id/stopbuild")
    def stop_build(self, id):
        project_id = int(id)
        try:
            ctx = self.server.context
            if hasattr(ctx, 'current_process') and ctx.current_process:
                pid = ctx.current_process.process.process.pid
                self.log("KILLING PROCESS AT %s" % pid)
                ctx.current_process.process.stop()
            else:
                return "NOTRUNNING"
            return "OK"
        except Exception, err:
            return "ERROR"

class BuildController(Controller):
    @route("/buildstatus")
    def buildstatus(self, *args, **kw):
        ctx = self.server.context
        projects = list(self.store.find(Project))
        projects_being_built = [int(project_id) for project_id in ctx.projects_being_built]
        result = {}
        for project in projects:
            if project.id in projects_being_built:
                result[project.id] = (project.name, "BUILDING")
            else:
                result[project.id] = (project.name, project.last_build is not None and "BUILT" or "UNKNOWN")

        return "\n".join(["%s=%s@@%s" % (k, v[0],v[1]) for k,v in result.items()])

    @route("/currentbuild")
    def current_build_report(self, **data):
        return self.render_template("current_build.html")

    @route("/currentbuild_mini")
    def current_build_report_mini(self, **data):
        return self.render_template("current_build_mini.html")

    @route("/currentstatus")
    def current_status(self, **data):
        ctx = self.server.context
        result = {}
        result['project'] = ctx.current_project and ctx.current_project.name or ''
        result['project_id'] = ctx.current_project and ctx.current_project.id or ''
        result['command'] = ctx.current_command
        result['log'] = ctx.current_log and u"<br />".join(unicode(ctx.current_log).splitlines()[-30:]) or ''

        return demjson.encode(result)

class PipelineController(Controller):
    @route("/pipeline", priority=5)
    def index(self):
        pipelines = list(self.store.find(Pipeline))
        return self.render_template("pipeline_index.html", pipeline=None, pipelines=pipelines, errors=None)

    @route("/pipeline/create")
    def create(self, name, pipeline_definition):
        pipeline = Pipeline(name)
        try:
            self.store.add(pipeline)

            pipeline.load_pipeline_items(pipeline_definition)

            self.server.publish("on_pipeline_created", {"server":self.server, "pipeline":pipeline})
            self.redirect("/pipeline")
        except (ProjectNotFoundError, CyclicalPipelineError), err:
            self.store.remove(pipeline)
            pipelines = list(self.store.find(Pipeline))
            return self.render_template("pipeline_index.html", pipeline=None, pipelines=pipelines, errors=[err.message,])

    @route("/pipeline/:id", priority=1)
    def edit(self, id):
        pipeline_id = int(id)
        pipelines = list(self.store.find(Pipeline))
        pipeline = self.store.get(Pipeline, pipeline_id)
        return self.render_template("pipeline_index.html", pipeline=pipeline, pipelines=pipelines, errors=None)

    @route("/pipeline/:id/update")
    def update(self, id, name, pipeline_definition):
        pipeline_id = int(id)
        pipeline = self.store.get(Pipeline, pipeline_id)

        errors = self.validate_pipe_definition(pipeline_definition)
        if errors:
            pipelines = list(self.store.find(Pipeline))
            return self.render_template("pipeline_index.html", pipeline=None, pipelines=pipelines, errors=errors)

        pipeline.name = name
        pipeline.items.clear()
        pipeline.load_pipeline_items(pipeline_definition)

        self.server.publish("on_pipeline_updated", {"server":self.server, "pipeline":pipeline})
        self.redirect('/pipeline')

    def validate_pipe_definition(self, pipeline_definition):
        errors = []
        all_projects = dict([(project.name, project) for project in list(self.store.find(Project))])

        pipeline_items = [item.strip().lower() for item in pipeline_definition.split(">")]

        for index, pipeline_item in enumerate(pipeline_items):
            key = pipeline_item
            if not all_projects.has_key(key):
                errors.append("The project with name %s does not exist" % key)

        cyclical_error = Pipeline.assert_for_cyclical_pipeline(pipeline_items)
        if cyclical_error:
            errors.append(cyclical_error)

        return errors

    @route("/pipeline/:id/delete")
    def delete(self, id):
        pipeline_id = int(id)
        pipeline = self.store.get(Pipeline, pipeline_id)
        for item in pipeline.items:
            self.store.remove(item)
        self.store.remove(pipeline)

        self.redirect('/pipeline')

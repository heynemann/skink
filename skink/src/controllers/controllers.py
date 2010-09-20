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
import template_filters

class IndexController(Controller):

    @route("/")
    def index(self):
        projects = self.store.query(Project).all()
        return self.render_template("index.html", projects=projects)

    @route("/twocolumns")
    def twocolumns(self):
        projects = self.store.query(Project).all()
        return self.render_template("twocolumns.html", projects=projects)

    @route("/threecolumns")
    def threecolumns(self):
        projects = self.store.query(Project).all()
        return self.render_template("threecolumns.html", projects=projects)


class ProjectController(Controller):

    @route("/project/new")
    def new(self):
        return self.render_template("add_project.html")

    @route("/project/create")
    def create(self, name, build_script, scm_repository, branch, **kwargs):
        monitor_changes = 'monitor_changes' in kwargs and kwargs['monitor_changes'] == 'MONITOR' or False
        prj = Project(name=name, 
                      build_script=build_script, 
                      scm_repository=scm_repository, 
                      monitor_changes=monitor_changes, 
                      branch=branch)
        self.store.add(prj)

        self.redirect("/")

    @route("/project/:id/edit")
    def edit(self, id):
        project_id = int(id)
        prj = self.store.query(Project).get(project_id)
        return self.render_template("edit_project.html", project=prj)

    @route("/project/:id/update")
    def update(self, id, name, build_script, scm_repository, branch, **kwargs):
        monitor_changes = 'monitor_changes' in kwargs and kwargs['monitor_changes'] == 'MONITOR' or False

        project_id = int(id)
        prj = self.store.query(Project).get(project_id)

        prj.name = name
        prj.branch = branch
        prj.build_script = build_script
        prj.scm_repository = scm_repository
        prj.monitor_changes = monitor_changes == "MONITOR"

        self.redirect("/project/%d" % project_id)

    @route("/project/:id", priority=1)
    def show_details(self, id):
        prj = self.store.query(Project).get(int(id))
        last_build = prj.last_build

        return self.render_template("project_details.html", project=prj, current_build=last_build)

    @route("/project/:id/builds/:build_id")
    def show_build_details(self, id, build_id):
        prj = self.store.query(Project).get(int(id))
        build = self.store.query(Build).get(int(build_id))

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

        prj = self.store.query(Project).get(project_id)

        pipelines = self.store.query(Pipeline, PipelineItem) \
                              .filter(PipelineItem.pipeline_id == Pipeline.id) \
                              .filter(PipelineItem.project_id == project_id) \
                              .all()

        for pipeline, pipeline_item in pipelines:
            for item in pipeline.items:
                self.store.delete(item)
            self.store.delete(pipeline)

        self.store.delete(prj)

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
            self.log("ERROR: %s while stoping project_id %d " % (err, project_id) )
            return "ERROR"

class BuildController(Controller):
    @route("/buildstatus")
    def buildstatus(self, *args, **kw):
        ctx = self.server.context

        projects = self.store.query(Project).all()

        projects_being_built = [int(project_id) for project_id in ctx.projects_being_built]
        results = []
        for project in projects:
            result = {}
            result['id'] = project.id
            result['name'] = project.name
            
            
            if project.id in projects_being_built:
                result['execution_status'] = "BUILDING"
            else:
                result['execution_status'] = "BUILT"
                
            if project.last_build is not None:
                result['status'] = project.last_build.status
                result['author'] = project.last_build.commit_author
                result['email'] = template_filters.email(project.last_build.commit_author)
                result['gravatar'] = template_filters.gravatar(project.last_build.commit_author)
                
                commit_text = project.last_build.commit_text[:50] 
                if len(project.last_build.commit_text) > 50:
                    commit_text = commit_text + "..."
                
                result['commit_text'] = commit_text
            else:
                result['status'] = 'UNKNOWN'
                    
            results.append(result)
        return demjson.encode(results)

    @route("/currentbuild")
    def current_build_report(self, **data):
        return self.render_template("current_build.html")


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
        pipelines = self.store.query(Pipeline).all()
        projects = self.store.query(Project).all()
        
        return self.render_template("pipeline_index.html", pipeline=None, pipelines=pipelines, projects=projects, errors=None)

    @route("/pipeline/create")
    def create(self, name, pipeline_definition):
        pipeline = Pipeline(name)
        try:
            pipeline.load_pipeline_items(pipeline_definition)

            self.store.add(pipeline)

            self.server.publish("on_pipeline_created", {"server":self.server, "pipeline":pipeline})
            self.redirect("/pipeline")
        except (ProjectNotFoundError, CyclicalPipelineError), err:
            pipelines = self.store.query(Pipeline).all()
            projects = self.store.query(Project).all()
            
            return self.render_template("pipeline_index.html", pipeline=None, pipelines=pipelines, projects=projects, errors=[err.message,])

    @route("/pipeline/:id", priority=1)
    def edit(self, id):
        pipeline_id = int(id)
        pipelines = self.store.query(Pipeline).all()
        pipeline = self.store.query(Pipeline).get(pipeline_id)
        projects = self.store.query(Project).all()
        
        return self.render_template("pipeline_index.html", pipeline=pipeline, pipelines=pipelines, projects=projects, errors=None)

    @route("/pipeline/:id/update")
    def update(self, id, name, pipeline_definition):
        pipeline_id = int(id)
        pipeline = self.store.query(Pipeline).get(pipeline_id)

        errors = self.validate_pipe_definition(pipeline_definition)
        if errors:
            pipelines = self.store.query(Pipeline).all()
            projects = self.store.query(Project).all()
            
            return self.render_template("pipeline_index.html", pipeline=None, pipelines=pipelines, projects=projects, errors=errors)

        pipeline.name = name

        for pipeline_item in pipeline.items:
            self.store.delete(pipeline_item)

        pipeline.load_pipeline_items(pipeline_definition)

        self.server.publish("on_pipeline_updated", {"server":self.server, "pipeline":pipeline})
        self.redirect('/pipeline')

    def validate_pipe_definition(self, pipeline_definition):
        errors = []
        all_projects = dict([(project.name.lower(), project) for project in self.store.query(Project).all()])

        pipeline_items = [item.strip().lower() for item in pipeline_definition.lower().split(">")]

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
        pipeline = self.store.query(Pipeline).get(pipeline_id)
        for item in pipeline.items:
            self.store.delete(item)
        self.store.delete(pipeline)

        self.redirect('/pipeline')
        
        
class MiniController(Controller):
    
    @route("/mini/")
    def mini(self):
        projects = self.store.query(Project).all()
        return self.render_template("mini.html", projects=projects)

    @route("/mini/currentbuild")
    def current_build_report_mini(self, **data):
        return self.render_template("current_build_mini.html")
            
    @route("/mini/twocolumns")
    def twocolumns(self):
        projects = self.store.query(Project).all()
        return self.render_template("twocolumns_mini.html", projects=projects)

    @route("/mini/threecolumns")
    def threecolumns(self):
        projects = self.store.query(Project).all()
        return self.render_template("threecolumns_mini.html", projects=projects)
        
    @route("/full")
    def full(self):
        return self.render_template("full.html")
            
            
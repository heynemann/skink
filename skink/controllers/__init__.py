#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.context import SkinkContext
from skink.imports import *
from skink.repositories import ProjectRepository, PipelineRepository
from skink.services import BuildService
from skink.errors import *
import template

class ProjectController(object):
    def __init__(self):
        self.repository = ProjectRepository()
        self.build_service = BuildService()
        
    @template.output("create_project.html")
    def new(self):
        return template.render(project=None)

    @template.output("create_project.html")
    def edit(self, project_id):
        project = self.repository.get(project_id)
        return template.render(project=project)

    def create(self, name, build_script, scm_repository, monitor_changes=None):
        project = self.repository.create(
                                name=name, 
                                build_script=build_script, 
                                scm_repository=scm_repository, 
                                monitor_changes=not monitor_changes is None)
        raise cherrypy.HTTPRedirect('/')

    def update(self, project_id, name, build_script, scm_repository, monitor_changes=None):
        project = self.repository.get(project_id)
        project.name = name
        project.build_script = build_script
        project.scm_repository = scm_repository
        project.monitor_changes = not monitor_changes is None
        self.repository.update(project)
        raise cherrypy.HTTPRedirect('/')

    def delete(self, project_id):
        project = self.repository.get(project_id)
        self.repository.delete(project_id)
        self.build_service.delete_scm_repository(project)
        raise cherrypy.HTTPRedirect('/')
    
    def build(self, project_id):
        print "Adding project %s to the queue" % project_id
        SkinkContext.current().build_queue.append(project_id)
        raise cherrypy.HTTPRedirect('/project/%s' % project_id)

    @template.output("project_details.html")
    def details(self, project_id):
        return self.render_details(project_id)

    @template.output("project_details.html")
    def build_details(self, project_id, build_id):
        return self.render_details(project_id, build_id)

    def render_details(self, project_id, build_id = None):
        project = self.repository.get(project_id)
        if not build_id:
            build = project.builds and project.builds[0] or None
        else:
            build = project.get_build_by_id(int(build_id))
        build_log = ""
        if build and build.log:
            build_log = highlight(build.log, BashLexer(), HtmlFormatter())
        return template.render(project=project, current_build=build, build_log=build_log)

class IndexController(object):
    @template.output("index.html")
    def index(self):
        repository = ProjectRepository()
        projects = repository.get_all()
        return template.render(projects=projects)
        
class PipelineController(object):
    def __init__(self):
        self.repository = PipelineRepository()
        
    @template.output("pipeline_index.html")
    def index(self):
        pipelines = self.repository.get_all()
        return template.render(pipeline=None, pipelines=pipelines, errors=None)
    
    @template.output("pipeline_index.html") 
    def create(self, name, pipeline_definition):
        pipelines = self.repository.get_all()
        try:
            self.repository.create(name, pipeline_definition)
            raise cherrypy.HTTPRedirect('/pipeline')
        except (ProjectNotFoundError, CyclicalPipelineError), err:
            return template.render(pipelines=pipelines, pipeline=None, errors=[err.message,]) | HTMLFormFiller(data=locals())

    @template.output("pipeline_index.html")
    def edit(self, pipeline_id):
        pipelines = self.repository.get_all()
        pipeline = self.repository.get(pipeline_id)
        return template.render(pipeline=pipeline, pipelines=pipelines, errors=None)

    @template.output("pipeline_index.html") 
    def update(self, pipeline_id, name, pipeline_definition):
        pipelines = self.repository.get_all()
        pipeline = self.repository.get(int(pipeline_id))
        try:
            self.repository.update(pipeline.id, name, pipeline_definition)
            raise cherrypy.HTTPRedirect('/pipeline')
        except (ProjectNotFoundError, CyclicalPipelineError), err:
            return template.render(pipelines=pipelines, pipeline=pipeline, errors=[err.message,]) | HTMLFormFiller(data=locals())
    
    def delete(self, pipeline_id):
        self.repository.delete(pipeline_id)
        raise cherrypy.HTTPRedirect('/pipeline')

#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

import cherrypy
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter

from skink.repositories import ProjectRepository
from skink.services import BuildService
import template

class ProjectController(object):
    def __init__(self):
        self.repository = ProjectRepository()
        self.build_service = BuildService()
        
    @template.output("create_project.html")
    def new(self):
        return template.render()

    def create(self, name, build_script, scm_repository):
        project = self.repository.create(name=name, build_script=build_script, scm_repository=scm_repository)
        raise cherrypy.HTTPRedirect('/')

    def delete(self, project_id):
        self.repository.delete(project_id)
        raise cherrypy.HTTPRedirect('/')
    
    def build(self, project_id):
        self.build_service.build_project(project_id)
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

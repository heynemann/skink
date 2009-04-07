#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

import cherrypy

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
        project = self.repository.get(project_id)
        return template.render(project=project, current_build=project.builds[-1])

    @template.output("project_details.html")
    def build_details(self, project_id, build_id):
        project = self.repository.get(project_id)
        return template.render(project=project, current_build=project.get_build_by_id(int(build_id)))

class IndexController(object):
    @template.output("index.html")
    def index(self):
        repository = ProjectRepository()
        projects = repository.get_all()
        return template.render(projects=projects)

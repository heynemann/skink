#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

import elixir

from skink.models import Project

class ProjectRepository(object):
    def create(self, name, build_script, scm_repository):
        '''Creates a new project.'''
        project = Project(name=name, build_script=build_script, scm_repository=scm_repository)
        elixir.session.commit()
        
        return project
        
    def get(self, project_id):
        return Project.query.filter_by(id=project_id).one()
    
    def get_all(self):
        return Project.query.all()
    
    def update(self, project):
        elixir.session.merge(project)
        elixir.session.commit()
        
    def delete(self, project_id):
        elixir.session.delete(self.get(project_id))
        elixir.session.commit()

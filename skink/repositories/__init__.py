#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.imports import *

from skink.models import Project, Pipeline, PipelineItem
from skink.errors import ProjectNotFoundError

class ProjectRepository(object):
    def create(self, name, build_script, scm_repository):
        '''Creates a new project.'''
        try:
            project = Project(name=name, build_script=build_script, scm_repository=scm_repository)
            elixir.session.commit()
        except:
            elixir.session.rollback()
            raise
        
        return project
        
    def get(self, project_id):
        return Project.query.filter_by(id=project_id).one()

    def get_project_by_name(self, project_name):
        return Project.query.filter_by(name=project_name).one()
    
    def get_all(self):
        return Project.query.all()

    def get_all_as_dictionary(self):
        all_projects = self.get_all()
        dictionary = dict(zip([project.name.lower() for project in all_projects], all_projects))
        return dictionary
    
    def update(self, project):
        try:
            elixir.session.merge(project)
            elixir.session.commit()
        except:
            elixir.session.rollback()
            raise        
    def delete(self, project_id):
        try:
            elixir.session.delete(self.get(project_id))
            elixir.session.commit()
        except:
            elixir.session.rollback()
            raise        
class PipelineRepository(object):
    def create(self, name, pipeline_definition):
        try:
            project_repository = ProjectRepository()
            pipeline = Pipeline()
            pipeline.name = name
            pipeline.load_pipeline_items(pipeline_definition, project_repository.get_all_as_dictionary())
            
            elixir.session.commit()
        except:
            elixir.session.rollback()
            raise
            
        return pipeline

    def update(self, pipeline_id, name, pipeline_definition):
        try:
            project_repository = ProjectRepository()
            pipeline = self.get(pipeline_id)
            self.__clear_pipeline_items(pipeline)
            pipeline.name = name
            pipeline.load_pipeline_items(pipeline_definition, project_repository.get_all_as_dictionary())
            
            elixir.session.commit()
        except:
            elixir.session.rollback()
            raise
            
        return pipeline

    def __clear_pipeline_items(self, pipeline):
        for pipeline_item in pipeline.items:
            pipeline_item.delete()
    
    def delete(self, pipeline_id):
        try:
            pipeline = self.get(pipeline_id)
            self.__clear_pipeline_items(pipeline)
            pipeline.delete()
            elixir.session.commit()
        except:
            elixir.session.rollback()
            raise
        
    def get(self, pipeline_id):
        return Pipeline.query.filter_by(id=pipeline_id).one()
        
    def get_all(self):
        return Pipeline.query.all()
        

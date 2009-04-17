#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.imports import *

from skink.models import Project, ProjectTab, Pipeline, PipelineItem
from skink.errors import ProjectNotFoundError

class BaseRepository(object):
    def commit(self):
        elixir.session.flush()
        elixir.session.commit()
    def rollback(self):
        elixir.session.rollback()

class ProjectRepository(BaseRepository):
    def create(self, name, build_script, scm_repository, monitor_changes, tabs):
        '''Creates a new project.'''
        try:
            project = Project(name=name, build_script=build_script, scm_repository=scm_repository, monitor_changes=monitor_changes)

            if tabs:
                for k,v in tabs.items():
                    if k and v:
                        tab = ProjectTab(name=k, command=v)
                        tab.project = project

            self.commit()
        except:
            self.rollback()
            raise
        
        return project
        
    def get(self, project_id):
        return Project.query.filter_by(id=project_id).one()

    def get_project_by_name(self, project_name):
        return Project.query.filter_by(name=project_name).one()
    
    def get_all(self):
        return Project.query.all()

    def get_projects_to_monitor(self):
        return Project.query.filter_by(monitor_changes=True).all()

    def get_all_as_dictionary(self):
        all_projects = self.get_all()
        dictionary = dict(zip([project.name.lower() for project in all_projects], all_projects))
        return dictionary

    def update(self, project, tabs):
        try:
            elixir.session.merge(project)
            if tabs:
                for tab in project.tabs:
                    tab.delete()
                for k,v in tabs.items():
                    if k and v:
                        tab = ProjectTab(name=k, command=v)
                        tab.project = project
            self.commit()
        except:
            self.rollback()
            raise

    def delete(self, project_id):
        try:
            pipeline_repository = PipelineRepository()
            project = self.get(project_id)
            pipelines = pipeline_repository.get_all_pipelines_for(project)
            for pipeline in pipelines:
                pipeline_repository.delete_pipeline(pipeline)
            elixir.session.delete(project)
            self.commit()
        except:
            self.rollback()
            raise

    #def start_build(self, project):
        #try:
            #project.build_status = "BUILDING"
            #self.commit()
        #except:
            #self.rollback()
            #raise

#    def finish_build(self, project):
#        try:
#            project.build_status = "BUILT"
#            self.commit()
#        except:
#            self.rollback()
#            raise

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
        pipeline = self.get(pipeline_id)
        self.delete_pipeline(pipeline)

    def delete_pipeline(self, pipeline):
        try:
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
        
    def get_all_pipelines_for(self, project):
        return Pipeline.query.filter(Pipeline.items.any(project=project)).all()
        

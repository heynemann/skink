#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.imports import *

from skink.models import Project, ProjectTab, Pipeline, PipelineItem, BuildTab, ProjectFileLocator, BuildFile
from skink.errors import ProjectNotFoundError

class ProjectRepository(object):
    def create(self, name, build_script, scm_repository, monitor_changes, tabs, file_locators):
        '''Creates a new project.'''
        project = Project(name=name,
                          build_script=build_script,
                          scm_repository=scm_repository,
                          monitor_changes=monitor_changes)

        if tabs:
            for tab in tabs:
                tab.project = project

        if file_locators:
            for locator in file_locators:
                file_locator = ProjectFileLocator(locator=locator, project=project)

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

    def get_build_tab_by_id(self, build_tab_id):
        return BuildTab.query.filter_by(id=build_tab_id).one()

    def get_build_file_by_id(self, build_file_id):
        return BuildFile.query.filter_by(id=build_file_id).one()

    def update(self, project, tabs, file_locators):

        while project.tabs:
            project.tabs.pop()
        while project.file_locators:
            project.file_locators.pop()

        if tabs:
            for tab in tabs:
                project.tabs.append(tab)

        if file_locators:
            for locator in file_locators:
                project.file_locators.append(ProjectFileLocator(locator=locator, project=project))

        elixir.session.merge(project)

    def delete(self, project_id):
        pipeline_repository = PipelineRepository()
        project = self.get(project_id)
        pipelines = pipeline_repository.get_all_pipelines_for(project)
        for pipeline in pipelines:
            pipeline_repository.delete_pipeline(pipeline)
        elixir.session.delete(project)

class PipelineRepository(object):
    def create(self, name, pipeline_definition):
        project_repository = ProjectRepository()
        pipeline = Pipeline()
        pipeline.name = name
        pipeline.load_pipeline_items(pipeline_definition, project_repository.get_all_as_dictionary())
        return pipeline

    def update(self, pipeline_id, name, pipeline_definition):
        project_repository = ProjectRepository()
        pipeline = self.get(pipeline_id)
        self.__clear_pipeline_items(pipeline)
        pipeline.name = name
        pipeline.load_pipeline_items(pipeline_definition, project_repository.get_all_as_dictionary())
        return pipeline

    def __clear_pipeline_items(self, pipeline):
        for pipeline_item in pipeline.items:
            pipeline_item.delete()
        
        while(len(pipeline.items)>0):
            pipeline.items.remove(pipeline.items[0])

    def delete(self, pipeline_id):
        pipeline = self.get(pipeline_id)
        self.delete_pipeline(pipeline)

    def delete_pipeline(self, pipeline):
        self.__clear_pipeline_items(pipeline)
        pipeline.delete()

    def get(self, pipeline_id):
        return Pipeline.query.filter_by(id=pipeline_id).one()

    def get_all(self):
        return Pipeline.query.all()

    def get_all_pipelines_for(self, project):
        return Pipeline.query.filter(Pipeline.items.any(project=project)).all()


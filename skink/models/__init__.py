#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.imports import *
from skink.errors import *

class Project(Entity):
    name = Field(Unicode(255))
    build_script = Field(Unicode(2000))
    scm_repository = Field(Unicode(1500))
    builds = OneToMany('Build', order_by="-date")
    pipeline_items = OneToMany('PipelineItem')
    using_options(tablename="projects")
            
    def get_build_by_id(self, build_id):
        for build in self.builds:
            if build.id == build_id:
                return build
        return None
    
    def get_last_build_number(self):
        if not hasattr(self, 'builds') or not self.builds:
            return 0
        return len(self.builds)

    def get_status(self):
        if not hasattr(self, 'builds') or not self.builds:
            return "UNKNOWN"
        return self.builds[0].status
    
    def get_last_successful_build(self):
        if not hasattr(self, 'builds') or not self.builds:
            return "UNKNOWN"
        for build in self.builds:
            if build.status=="SUCCESS":
                return "#%s (%s)" % (build.number, build.date.strftime("%m/%d/%Y %H:%M:%S"))

        return "NONE"

class Build(Entity):
    number = Field(Integer)
    date = Field(DateTime)
    status = Field(Unicode(20))
    scm_status = Field(Unicode(20))
    log = Field(Unicode(4000))
    commit_number = Field(Unicode(40))
    commit_author = Field(Unicode(400))
    commit_committer = Field(Unicode(400))
    commit_text = Field(Unicode(4000))
    commit_author_date = Field(DateTime)
    commit_committer_date = Field(DateTime)
    project = ManyToOne('Project')
    using_options(tablename="builds")

    def html_commit_text(self):
        return self.commit_text and self.commit_text.strip().replace("\n","<br />") or ""
        
class Pipeline(Entity):
    name = Field(Unicode(100))
    items = OneToMany('PipelineItem')
    using_options(tablename="pipelines")
    
    def load_pipeline_items(self, pipeline_definition, all_projects):
        pipeline_items = pipeline_definition.split(">")

        for pipeline_item in pipeline_items:
            key = pipeline_item.strip().lower()
            if not all_projects.has_key(key):
                raise ProjectNotFoundError("The project with name %s does not exist" % key)
            project = all_projects[key]
            pipeline_item = PipelineItem()
            pipeline_item.pipeline = self
            pipeline_item.project = project
    
    def __str__(self):
        if not self.items:
            return "No items in the pipeline."
        items_description = []
        for pipeline_item in self.items:
            items_description.append(pipeline_item.project.name)
        
        return " > ".join(items_description)

class PipelineItem(Entity):
    pipeline = ManyToOne('Pipeline')
    project = ManyToOne('Project')


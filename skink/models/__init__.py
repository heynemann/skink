#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import re
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.imports import *
from skink.errors import *

class Project(Entity):
    name = Field(Unicode(255))
    build_script = Field(Unicode(2000))
    scm_repository = Field(Unicode(1500))
    #builds = OneToMany('Build', order_by="-date", lazy=True)
    tabs = OneToMany('ProjectTab', order_by="name")
    file_locators = OneToMany('ProjectFileLocator')
    pipeline_items = OneToMany('PipelineItem')
    monitor_changes = Field(Boolean)
    build_status = Field(Unicode(15), default="UNKNOWN")
    using_options(tablename="projects")
    
    @property
    def last_builds(self):
        return Build.query.filter_by(project=self).order_by('-date').all()[:10]
            
    def get_build_by_id(self, build_id):
        for build in self.last_builds:
            if build.id == build_id:
                return build
        return None
    
    def get_last_build_number(self):
        if not hasattr(self, 'builds') or not self.last_builds:
            return 0
        return len(self.last_builds)

    def get_last_build(self):
        if not hasattr(self, 'builds') or not self.last_builds:
            return None
        return self.last_builds[0]

    def get_status(self):
        if not hasattr(self, 'builds') or not self.last_builds:
            return "UNKNOWN"
        return self.last_builds[0].status
    
    def get_last_successful_build(self):
        if not hasattr(self, 'builds') or not self.last_builds:
            return "UNKNOWN"
        for build in self.last_builds:
            if build.status=="SUCCESS":
                return "#%s (%s)" % (build.number, build.date.strftime("%m/%d/%Y %H:%M:%S"))

        return "NONE"

    def to_dict(self):
        last_build = self.get_last_build()
        values = {}
        values["id"] = self.id
        values["name"] = self.name
        values["lastBuild"] = (last_build == None and "''" or last_build.to_dict())
        return values

class ProjectTab(Entity):
    name = Field(Unicode(255))
    command = Field(Unicode(2000))
    content_type = Field(Unicode(100))
    project = ManyToOne('Project')
    using_options(tablename="project_tabs")

class ProjectFileLocator(Entity):
    locator = Field(Unicode(255))
    project = ManyToOne('Project')
    using_options(tablename="project_file_locators")

class Build(Entity):
    number = Field(Integer)
    date = Field(DateTime)
    status = Field(Unicode(20))
    scm_status = Field(Unicode(20))
    log = Field(UnicodeText, deferred=True)
    commit_number = Field(Unicode(40))
    commit_author = Field(Unicode(400))
    commit_committer = Field(Unicode(400), deferred=True)
    commit_text = Field(UnicodeText)
    commit_author_date = Field(DateTime)
    commit_committer_date = Field(DateTime)
    project = ManyToOne('Project')
    tabs = OneToMany('BuildTab', order_by="name")
    files = OneToMany('BuildFile', order_by="name")
    using_options(tablename="builds")

    def commit_author_name(self):
        regex = r'\s[<][^<]+[>]$'
        return re.sub(regex, '', self.commit_author)

    def html_commit_text(self):
        return self.commit_text and self.commit_text.strip().replace("\n","<br />") or ""
    
    def to_dict(self):
        values = {}
        values["number"] = self.number
        values["date"] = self.date.strftime("%d/%m/%Y %H:%M:%S")
        values["status"] = self.status
        values["commitNumber"] = self.commit_number
        values["commitAuthor"] = self.commit_author
        values["commitAuthorDate"] = self.commit_author_date.strftime("%d/%m/%Y %H:%M:%S")
        values["commitCommitter"] = self.commit_author
        values["commitCommitterDate"] = self.commit_committer_date.strftime("%d/%m/%Y %H:%M:%S")
        values["commitText"] = self.commit_text.replace("\"", "'")
        return values

class BuildTab(Entity):
    name = Field(Unicode(255))
    command = Field(Unicode(2000))
    content_type = Field(Unicode(100))
    build = ManyToOne('Build')
    log = Field(UnicodeText)
    using_options(tablename="build_tabs")

class BuildFile(Entity):
    name = Field(Unicode(255))
    original_path = Field(Unicode(2000))
    content = Field(Binary)
    build = ManyToOne('Build')
    using_options(tablename="build_files")

class Pipeline(Entity):
    name = Field(Unicode(100))
    items = OneToMany('PipelineItem', order_by='id')
    using_options(tablename="pipelines")

    def load_pipeline_items(self, pipeline_definition, all_projects):
        pipeline_items = [item.strip().lower() for item in pipeline_definition.split(">")]
        
        self.assert_for_cyclical_pipeline(pipeline_items)
        
        for pipeline_item in pipeline_items:
            key = pipeline_item
            if not all_projects.has_key(key):
                raise ProjectNotFoundError("The project with name %s does not exist" % key)
            project = all_projects[key]
            pipeline_item = PipelineItem()
            pipeline_item.pipeline = self
            pipeline_item.project = project

    def assert_for_cyclical_pipeline(self, pipeline_items):
        added_items = []
        repeated_items = []
        for item in pipeline_items:
            if item in added_items:
                repeated_items.append(item)
            else:
                added_items.append(item)
        
        if repeated_items:
            raise CyclicalPipelineError("You are trying to create a cyclical pipeline. \nRepeated projects: %s" % ", ".join(repeated_items))
            
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
    using_options(tablename="pipeline_items")


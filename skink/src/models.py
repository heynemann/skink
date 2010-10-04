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

from sqlalchemy import Column, Integer, Unicode, DateTime, Boolean, ForeignKey, desc, Text
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base

from ion.sqlalchemy_tool import *

from skink.src.errors import *

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    build_script = Column(Unicode)
    branch = Column(Unicode)
    scm_repository = Column(Unicode)
    monitor_changes = Column(Boolean)

    def __init__(self, name, build_script, scm_repository, branch, monitor_changes):
        self.name = name
        self.build_script = build_script
        self.scm_repository = scm_repository
        self.monitor_changes = monitor_changes
        self.branch = branch

    @property
    def build_status(self):
        l_build = self.last_build
        if l_build:
            return l_build.status
        return "Unknown"

    @property
    def last_build(self):
        l_build = session.query(Build).filter(Build.project==self).order_by(desc(Build.id)).first()
        if not l_build:
            return None
        return l_build

    @property
    def last_builds(self):
        builds = session.query(Build).filter(Build.project==self).order_by(desc(Build.id))[:10]

        if not builds:
            return []
        return builds

class Build(Base):
    __tablename__ = "builds"

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    build_date = Column(DateTime)
    status = Column(Integer)
    scm_status = Column(Integer)
    log = Column(Text)
    commit_number = Column(Unicode)
    commit_author = Column(Unicode)
    commit_committer = Column(Unicode)
    commit_text = Column(Unicode)
    commit_author_date = Column(DateTime)
    commit_committer_date = Column(DateTime)

    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relation(Project, primaryjoin=project_id == Project.id)

    def __init__(self,
                 number,
                 build_date,
                 status,
                 scm_status,
                 log,
                 commit_number,
                 commit_author,
                 commit_committer,
                 commit_text,
                 commit_author_date,
                 commit_committer_date,
                 project):
        self.number = number
        self.build_date = build_date
        self.status = status
        self.scm_status = scm_status
        self.log = log
        self.commit_number = commit_number
        self.commit_author = commit_author
        self.commit_committer = commit_committer
        self.commit_text = commit_text
        self.commit_author_date = commit_author_date
        self.commit_committer_date = commit_committer_date
        self.project = project

class BuildTab(Base):
    __tablename__ = "build_tabs"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    content_type = Column(Unicode)
    log = Column(Unicode)

    build_id = Column(Integer, ForeignKey('builds.id'))
    build = relation(Build, primaryjoin=build_id == Build.id)

    def __init__(self, name, log, build, content_type="html"):
        self.name = name
        self.content_type = content_type
        self.log = log
        self.build = build

class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)

    def __init__(self, name):
        self.name = name

    def load_pipeline_items(self, pipeline_definition):
        all_projects = dict([(project.name.lower(), project) for project in session.query(Project).all()])

        pipeline_items = [item.strip().lower() for item in pipeline_definition.split(">")]

        Pipeline.assert_for_cyclical_pipeline(pipeline_items)

        for index, pipeline_item in enumerate(pipeline_items):
            key = pipeline_item
            if not all_projects.has_key(key):
                raise ProjectNotFoundError("The project with name %s does not exist" % key)
            project = all_projects[key]
            pipeline_item = PipelineItem()
            pipeline_item.order = index
            pipeline_item.project = project

            self.items.append(pipeline_item)

    @classmethod
    def assert_for_cyclical_pipeline(cls, pipeline_items):
        added_items = []
        repeated_items = []
        for item in pipeline_items:
            if item in added_items:
                repeated_items.append(item)
            else:
                added_items.append(item)

        if repeated_items:
            return "You are trying to create a cyclical pipeline. \nRepeated projects: %s" % ", ".join(repeated_items)

        return None

    def __str__(self):
        if not self.items:
            return "No items in the pipeline."
        items_description = []
        for pipeline_item in self.items:
            items_description.append(pipeline_item.project.name)

        return " > ".join(items_description)

class PipelineItem(Base):
    __tablename__ = "pipeline_items"

    id = Column(Integer, primary_key=True)

    order = Column(Integer)

    pipeline_id = Column(Integer, ForeignKey('pipelines.id'))
    pipeline = relation(Pipeline, primaryjoin=pipeline_id == Pipeline.id)

    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relation(Project, primaryjoin=project_id == Project.id)

#Collections
Project.builds = relation(Build)
Pipeline.items = relation(PipelineItem, order_by=PipelineItem.order)
Build.tabs = relation(BuildTab)


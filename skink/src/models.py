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

from storm.locals import *
from skink.src.errors import *

class Project(object):
    __storm_table__ = "projects"

    id = Int(primary=True)
    name = Unicode()
    build_script = Unicode()
    scm_repository = Unicode()
    monitor_changes = Bool()

    def __init__(self, name, build_script, scm_repository, monitor_changes):
        self.name = name
        self.build_script = build_script
        self.scm_repository = scm_repository
        self.monitor_changes = monitor_changes

    @property
    def build_status(self):
        if self.builds.count():
            return self.last_build.status
        return "Unknown"

    @property
    def last_build(self):
        builds = list(Store.of(self).find(Build, Build.project == self).order_by(Desc(Build.id))[:1])
        return builds and builds[0] or None

    @property
    def last_builds(self):
        builds = list(Store.of(self).find(Build, Build.project == self).order_by(Desc(Build.id))[:10])
        return builds

class Build(object):
    __storm_table__ = "builds"

    id = Int(primary=True)
    number = Int()
    build_date = DateTime()
    status = Enum(map={"Unknown": "0", "Successful": "1", "Failed": "2"})
    scm_status = Enum(map={"Created": "0", "Updated": "1", "Failed": "2"})
    log = Unicode()
    commit_number = Unicode()
    commit_author = Unicode()
    commit_committer = Unicode()
    commit_text = Unicode()
    commit_author_date = DateTime()
    commit_committer_date = DateTime()

    project_id = Int()
    project = Reference(project_id, Project.id)

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

class Pipeline(object):
    __storm_table__ = "pipelines"

    id = Int(primary=True)
    name = Unicode()

    def __init__(self, name):
        self.name = name

    def load_pipeline_items(self, pipeline_definition):
        all_projects = dict([(project.name, project) for project in list(Store.of(self).find(Project))])

        pipeline_items = [item.strip().lower() for item in pipeline_definition.split(">")]

        Pipeline.assert_for_cyclical_pipeline(pipeline_items)

        for index, pipeline_item in enumerate(pipeline_items):
            key = pipeline_item
            if not all_projects.has_key(key):
                raise ProjectNotFoundError("The project with name %s does not exist" % key)
            project = all_projects[key]
            pipeline_item = PipelineItem()
            pipeline_item.order = index
            pipeline_item.pipeline = self
            pipeline_item.project = project

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
        for pipeline_item in list(Store.of(self).find(PipelineItem, PipelineItem.pipeline_id==self.id).order_by(PipelineItem.order)):
            items_description.append(pipeline_item.project.name)

        return " > ".join(items_description)

class PipelineItem(object):
    __storm_table__ = "pipeline_items"

    id = Int(primary=True)

    order = Int()

    pipeline_id = Int()
    pipeline = Reference(pipeline_id, Pipeline.id)

    project_id = Int()
    project = Reference(project_id, Project.id)

#Collections
Project.builds = ReferenceSet(Project.id, Build.project_id)
Pipeline.items = ReferenceSet(Pipeline.id, PipelineItem.pipeline_id)


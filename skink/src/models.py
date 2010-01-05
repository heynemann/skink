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

class Project(object):
    __storm_table__ = "projects"

    id = Int(primary=True)
    name = Unicode()
    build_script = Unicode()
    scm_repository = Unicode()
    monitor_changes = Bool()
    build_status = Enum(map={"UNKNOWN": "0", "SUCCESSFUL": "1", "FAILED": "2"})

    def __init__(self, name, build_script, scm_repository, monitor_changes):
        self.name = name
        self.build_script = build_script
        self.scm_repository = scm_repository
        self.monitor_changes = monitor_changes
        self.build_status = "UNKNOWN"

class Build(object):
    __storm_table__ = "builds"

    id = Int(primary=True)
    number = Int()
    build_date = DateTime()
    status = Enum(map={"Unknown": "0", "Successful": "1", "Failed": "2"})
    scm_status = Enum(map={"Unknown": "0", "Successful": "1", "Failed": "2"})
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


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

from datetime import datetime

import skink.lib
from base import *
from skink.src.models import Project, Build

store = None

def clear():
    global store
    store = create_store()
    create_models(store)

def test_can_create_project():
    global store
    clear()
    proj = Project(name=u"Test Project 1", build_script=u"test build script", scm_repository=u"scm_repository", monitor_changes=False, branch="master")

    store.add(proj)

    store.commit()

    found_proj = store.query(Project).filter(Project.name == u"Test Project 1").one()

    assert found_proj.id
    assert found_proj.id == proj.id

def test_can_create_build():
    global store
    clear()
    some_date = datetime.now()
    proj = Project(name=u"Test Project 1", build_script=u"test build script", scm_repository=u"scm_repository", monitor_changes=False, branch="master")

    build = Build(number=1,
                  build_date=some_date,
                  status="Successful",
                  scm_status="Successful",
                  log=u"some_log",
                  commit_number=u"commit_number",
                  commit_author=u"commit_author",
                  commit_committer=u"commit_committer",
                  commit_text=u"commit_text",
                  commit_author_date=some_date,
                  commit_committer_date=some_date,
                  project=proj)

    store.add(build)
    store.commit()

    found_build = store.query(Build).filter(Build.project == proj).one()

    assert found_build.id
    assert found_build.id == build.id

    assert found_build.project is proj


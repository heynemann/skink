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

from skink.src.models import *

def test_can_create_project():
    proj = Project(name=u"Test Project 1", build_script=u"test build script", scm_repository=u"scm_repository", monitor_changes=False)

    assert proj.name == u"Test Project 1"
    assert proj.build_script == u"test build script"
    assert proj.scm_repository == u"scm_repository"
    assert proj.monitor_changes == False

def test_can_create_builds():
    some_date = datetime.now()

    proj = Project(name=u"Test Project 2", build_script=u"test build script", scm_repository=u"scm_repository", monitor_changes=False)

    build = Build(number=1, 
                  date=some_date,
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

    assert build.number == 1
    assert build.date == some_date
    assert build.status == "Successful"
    assert build.scm_status == "Successful"
    assert build.log == "some_log"
    assert build.commit_number == "commit_number"
    assert build.commit_author == "commit_author"
    assert build.commit_committer == "commit_committer"
    assert build.commit_text == "commit_text"
    assert build.commit_author_date == some_date
    assert build.commit_committer_date == some_date
    assert build.project == proj


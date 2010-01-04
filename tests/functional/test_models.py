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

from base import *

from skink.src.models import Project

store = create_store()
create_models(store)

def test_can_create_project():
    proj = Project(name=u"Test Project 1", build_script=u"test build script", scm_repository=u"scm_repository", monitor_changes=False)

    store.add(proj)

    store.commit()

    found_proj = store.find(Project, Project.name == u"Test Project 1").one()

    assert found_proj.id
    assert found_proj.id == proj.id


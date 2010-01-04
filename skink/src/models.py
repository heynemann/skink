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

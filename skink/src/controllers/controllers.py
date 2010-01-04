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
from ion.controllers import Controller, route, authenticated
from skink.src.models import *

class IndexController(Controller):

    @route("/")
    def index(self):
        projects = list(self.store.find(Project))
        return self.render_template("index.html", projects=projects)

class ProjectController(Controller):

    @route("/project/new")
    def new(self):
        return self.render_template("add_project.html")

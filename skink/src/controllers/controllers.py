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

    @route("/project/create")
    def create(self, name, build_script, scm_repository, monitor_changes=None):
        prj = Project(name=name, build_script=build_script, scm_repository=scm_repository, monitor_changes=monitor_changes == "MONITOR")
        self.store.add(prj)

        self.redirect("/")

    @route("/project/:id")
    def show_details(self, id):
        prj = self.store.get(Project, int(id))

        return self.render_template("project_details.html", project=prj)

    @route("/project/:id/build")
    def build(self, id):
        project_id = int(id)
        self.log("Adding project %s to the queue" % project_id)
        self.context.build_queue.append(project_id)
        self.redirect('/project/%s' % project_id)

class BuildController(Controller):
    @route("/buildstatus")
    def buildstatus(self, *args, **kw):
        ctx = self.server.context
        projects = list(self.store.find(Project))
        projects_being_built = [int(project_id) for project_id in ctx.projects_being_built]
        result = {}
        for project in projects:
            if project.id in projects_being_built:
                result[project.id] = (project.name, "BUILDING")
            else:
                result[project.id] = (project.name, project.last_build is not None and "BUILT" or "UNKNOWN")

        return "\n".join(["%s=%s@@%s" % (k, v[0],v[1]) for k,v in result.items()])


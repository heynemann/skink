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

from os.path import exists, join, dirname, abspath

import skink.lib
import cherrypy

from skink.src.services.executers import ShellExecuter

class GitService(object):
    def log(self, message):
        ctx = self.server.context
        if ctx.settings.Ion.verbose:
            cherrypy.log(message, '[GITSERVICE]')

    def __init__(self, server):
        self.server = server
        self.base_dir = self.server.build_dir

    def fix_name(self, name):
        return name.strip().replace(" ", "")

    def is_repository_created(self, path):
        if not exists(path) or not exists(join(path, ".git")):
            return False
        return True
    
    def does_project_need_update(self, project):
        executer = ShellExecuter(verbose=self.server.context.settings.Ion.as_bool("verbose"))
        project_name = self.fix_name(project.name)
        repository_path = join(self.base_dir, project_name)
        is_repo_created = self.is_repository_created(repository_path)
        if not is_repo_created:
            self.log("The repository at %s needs to be created." % repository_path)
            return True
        
        self.log("Verifying if the repository at %s needs to be updated" % repository_path)
        executer.execute("git remote update", repository_path)
        result = executer.execute("git rev-parse origin/master master", repository_path)
        commits = result.run_log.split()
        return len(commits) != 2 or commits[0]!=commits[1]

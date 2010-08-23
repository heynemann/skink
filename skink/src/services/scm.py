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

import sys
import os
import time
from datetime import datetime
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
        result = executer.execute("git rev-parse origin/%s %s" % (project.branch, project.branch), repository_path)
        commits = result.run_log.split()
        return len(commits) != 2 or commits[0]!=commits[1]

    def create_or_update(self, project):
        executer = ShellExecuter(verbose=self.server.context.settings.Ion.as_bool("verbose"))
        project_name = self.fix_name(project.name)
        repository_path = join(self.base_dir, project_name)
        is_repo_created = self.is_repository_created(repository_path)
        if not is_repo_created and exists(repository_path):
            raise ValueError("The specified directory(%s) is not empty and is not a git repository")
        if not is_repo_created:
            if not exists(self.base_dir):
                try:
                    os.mkdir(self.base_dir)
                except:
                    raise ValueError("Could not create folder %s" % self.base_dir)
                self.log("Directory successfully created.")

            self.log("Retrieving scm data for project %s in repository %s (creating new repository - clone)" % (project_name, project.scm_repository))
            result = executer.execute("git clone %s %s && cd %s && git checkout -t origin/%s" % (project.scm_repository, project_name, project_name, project.branch), self.base_dir)
            if result.exit_code == 0:
                self.log("SCM Data retrieved successfully")
            else:
                self.log("Error retrieving SCM Data: %s" % result.run_log)
            last_commit = self.get_last_commit(repository_path)
            return ScmResult(result.exit_code == 0 and ScmResult.Created or ScmResult.Failed, repository_path, last_commit, result.run_log)
        else:
            self.log("Retrieving scm data for project %s in repository %s (updating repository - pull)" % (project_name, project.scm_repository))
            result = executer.execute("git branch | grep %s" % project.branch, repository_path)
            if project.branch in result.run_log:
                result = executer.execute("git checkout %s" % project.branch, repository_path)
            else:
                result = executer.execute("git checkout -t origin/%s" % project.branch, repository_path)
                
            result = executer.execute("git reset --hard", repository_path)
            result = executer.execute("git clean -df", repository_path)
            result = executer.execute("git pull origin %s" % project.branch, repository_path)
            if result.exit_code == 0:
                self.log("SCM Data retrieved successfully")
            else:
                self.log("Error retrieving SCM Data: %s" % result.run_log)
            
            self.log("Retrieving last commit data for project %s in repository %s" % (project_name, project.scm_repository))
            last_commit = self.get_last_commit(repository_path)
            self.log("Data retrieved.")
            return ScmResult(result.exit_code == 0 and ScmResult.Updated or ScmResult.Failed, repository_path, last_commit, result.run_log)

    def get_last_commit(self, repository_path):
        commit_number = None
        author = None
        committer = None

        command = "git show -s --pretty=format:'%H||%an||%ae||%ai||%cn||%ce||%ci||%s'"

        executer = ShellExecuter()
        result = executer.execute(command, repository_path)

        if result.exit_code != 0:
            raise ValueError("unable to determine last commit. Error: %s" % result.run_log)
        commit_number, author_name, author_email, author_date, committer_name, committer_email, committer_date, subject = result.run_log.split("||")

        author_date = self.convert_to_date(author_date)
        committer_date = self.convert_to_date(committer_date)

        return {
                   'commit_number': commit_number,
                   'author': "%s <%s>" % (author_name, author_email),
                   'author_date': author_date,
                   'committer': "%s <%s>" % (committer_name, committer_email),
                   'committer_date': committer_date,
                   'subject': subject
               }

    def convert_to_date(self, dt):
        dt = " ".join(dt.split(" ")[:2])
        time_components = time.strptime(dt.strip(), "%Y-%m-%d %H:%M:%S")[:6]
        now = datetime(*time_components)
        return now

class ScmResult(object):
    Created = u"Created"
    Updated = u"Updated"
    Failed = u"Failed"
    
    def __init__(self, status, repository_path, last_commit, log):
        self.status = status
        self.repository_path = repository_path
        self.last_commit = last_commit
        self.log = log


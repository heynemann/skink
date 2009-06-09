#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join, exists
import os
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

import re
import shutil
from datetime import datetime
import time

from skink.context import SkinkContext
from executers import ShellExecuter

class GitRepository(object):
    def log(self, message):
        ctx = SkinkContext.current()
        if ctx.scm_verbose:
            print message

    def __init__(self, base_dir):
        self.base_dir = base_dir

    def create_or_update(self, project):
        executer = ShellExecuter()
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
            result = executer.execute("git clone %s %s" % (project.scm_repository, project_name), self.base_dir)
            if result.exit_code == 0:
                self.log("SCM Data retrieved successfully")
            else:
                self.log("Error retrieving SCM Data: %s" % result.run_log)
            last_commit = self.get_last_commit(repository_path)
            return ScmResult(result.exit_code == 0 and ScmResult.Created or ScmResult.Failed, repository_path, last_commit, result.run_log)
        else:
            self.log("Retrieving scm data for project %s in repository %s (updating repository - pull)" % (project_name, project.scm_repository))
            result = executer.execute("git pull", repository_path)
            if result.exit_code == 0:
                self.log("SCM Data retrieved successfully")
            else:
                self.log("Error retrieving SCM Data: %s" % result.run_log)
            
            self.log("Retrieving last commit data for project %s in repository %s" % (project_name, project.scm_repository))
            last_commit = self.get_last_commit(repository_path)
            self.log("Data retrieved.")
            return ScmResult(result.exit_code == 0 and ScmResult.Updated or ScmResult.Failed, repository_path, last_commit, result.run_log)

    def is_repository_created(self, path):
        if not exists(path) or not exists(join(path, ".git")):
            return False
        return True
    
    def does_project_need_update(self, project):
        executer = ShellExecuter()
        project_name = self.fix_name(project.name)
        repository_path = join(self.base_dir, project_name)
        is_repo_created = self.is_repository_created(repository_path)
        if not is_repo_created:
            self.log("The repository at %s needs to be created." % repository_path)
            return True
        
        self.log("Verifying if the repository at %s needs to be updated" % repository_path)
        executer.execute("git remote update", repository_path)
        result = executer.execute("git rev-parse origin master", repository_path)
        commits = result.run_log.split()
        return len(commits) != 2 or commits[0]!=commits[1]

    def remove_repository(self, project):
        project_name = self.fix_name(project.name)
        repository_path = join(self.base_dir, project_name)
        is_repo_created = self.is_repository_created(repository_path)
        if not is_repo_created:
            return None
        
        shutil.rmtree(repository_path)

    def fix_name(self, name):
        return name.strip().replace(" ", "")

    def get_last_commit(self, repository_path):
        commit_number = None
        author = None
        committer = None

        command = "git show -s --pretty=format:\"%H||%an||%ae||%ai||%cn||%ce||%ci||%s\""
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
    Created = u"CREATED"
    Updated = u"UPDATED"
    Failed = u"FAILED"
    
    def __init__(self, status, repository_path, last_commit, log):
        self.status = status
        self.repository_path = repository_path
        self.last_commit = last_commit
        self.log = log


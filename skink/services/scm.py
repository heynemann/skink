#!/usr/bin/env python
# -*- coding:utf-8 -*-
from os.path import join, exists
from executers import ShellExecuter
import re

class GitRepository(object):
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
                result = executer.execute("mkdir %s" % self.base_dir, self.base_dir, change_dir=False)
                if result.exit_code != 0:
                    raise ValueError("Could not create folder %s" % self.base_dir)
            result = executer.execute("git clone %s %s" % (project.scm_repository, project_name), self.base_dir)
            last_commit = self.get_last_commit(repository_path)
            return ScmResult(result.exit_code == 0 and ScmResult.Created or ScmResult.Failed, repository_path, last_commit)
        else:
            result = executer.execute("git pull", repository_path)
            last_commit = self.get_last_commit(repository_path)
            return ScmResult(result.exit_code == 0 and ScmResult.Updated or ScmResult.Failed, repository_path, last_commit)

    def is_repository_created(self, path):
        if not exists(path) or not exists(join(path, ".git")):
            return False
        return True

    def fix_name(self, name):
        return name.strip().replace(" ", "")

    def get_last_commit(self, repository_path):
        commit_number = None
        author = None
        committer = None
        
        command = "git log | egrep '^commit' | sed 's/commit //g' | sed -n 1p | git show -s --pretty=raw"
        executer = ShellExecuter()
        result = executer.execute(command, repository_path)
        
        regexp = re.compile("^commit ([\w\d]+\n)tree ([\w\d]+\n)parent ([\w\d]+\n)author ([\w\d\s<@.]+>).+\ncommitter ([\w\d\s<@.]+>).+\n([^$]+)")
        data = regexp.match(result.run_log)
        groups = data.groups()
        commit_number = groups[0]
        author = groups[3]
        committer = groups[4]
        text = groups[5]

        return (commit_number, author, committer, text)
        
class ScmResult(object):
    Created = "CREATED"
    Updated = "UPDATED"
    Failed = "FAILED"
    
    def __init__(self, status, repository_path, last_commit):
        self.status = status
        self.repository_path = repository_path
        self.last_commit = last_commit


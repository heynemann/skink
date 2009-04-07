#!/usr/bin/env python
# -*- coding:utf-8 -*-
from os.path import join, exists
from executers import ShellExecuter

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
            return ScmResult(result.exit_code == 0 and ScmResult.Created or ScmResult.Failed, repository_path)
        else:
            result = executer.execute("git pull", self.base_dir)
            return ScmResult(result.exit_code == 0 and ScmResult.Updated or ScmResult.Failed, repository_path)

    def is_repository_created(self, path):
        if not exists(path) or not exists(join(path, ".git")):
            return False
        return True

    def fix_name(self, name):
        return name.strip().replace(" ", "")

class ScmResult(object):
    Created = "CREATED"
    Updated = "UPDATED"
    Failed = "FAILED"
    
    def __init__(self, status, repository_path):
        self.status = status
        self.repository_path = repository_path


#!/usr/bin/env python
#-*- coding:utf-8 -*-
from datetime import datetime
import sys
from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.models import Build
from skink.repositories import ProjectRepository
from skink.services.scm import GitRepository, ScmResult
from skink.services.executers import ShellExecuter
from skink.context import SkinkContext

class BuildService(object):
    Success = "SUCCESS"
    Failure = "FAILURE"
    
    def __init__(self, repository=None, scm=None, executer=None, base_path=join(root_path, SkinkContext.current().build_path)):
        if not repository:
            self.repository = ProjectRepository()
        else:
            self.repository = repository
            
        if not scm:
            self.scm = GitRepository(base_path)
        else:
            self.scm = scm
            
        if not executer:
            self.executer = ShellExecuter()
        else:
            self.executer = executer
        
        self.base_path = base_path

    def build_project(self, project_id):
        log = ["Build started at %s" % datetime.now()]

        status = BuildService.Failure
        scm_status = ScmResult.Failed
        project = self.repository.get(project_id)
        build = Build()
        build.date = datetime.now()
        build.status = status
        build.scm_status = scm_status
        build.log = ""
        build.project = project

        last_build_number = project.get_last_build_number()
        
        scm_creation_result = self.scm.create_or_update(project)
        build.scm_status = scm_creation_result.status
        if scm_creation_result.status == ScmResult.Failed:
            log.append(scm_creation_result.log)
            status = BuildService.Failure
        else:
            log.append("Downloaded code from %s" % project.scm_repository)
            
            execute_result = self.executer.execute(project.build_script, scm_creation_result.repository_path)
            log.append("Executed %s" % project.build_script)
            log.append("Exit Code: %s" % execute_result.exit_code)
            log.append("Run Log:")
            log.append(execute_result.run_log)
            
            status = execute_result.exit_code == 0 and BuildService.Success or BuildService.Failure
        
        build.number = last_build_number + 1
        build.status = status
        build.log = "\n".join(log)
        build.commit_number = scm_creation_result.last_commit[0]
        build.commit_author = scm_creation_result.last_commit[1]
        build.commit_committer = scm_creation_result.last_commit[2]
        build.commit_text = scm_creation_result.last_commit[3]
        
        self.repository.update(project)
        
        return build

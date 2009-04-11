#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import os
from os.path import dirname, abspath, join
import unittest
import shutil
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from tests.base.base_functional_test import BaseFunctionalTest
from skink.models import Project
from skink.repositories import ProjectRepository
from skink.services import BuildService
from skink.services.executers import ShellExecuter, ExecuteResult
from skink.services.scm import GitRepository, ScmResult

class TestBuildService(BaseFunctionalTest):

    def test_build_successfully(self):
        project = self.create_project(name="pyoc", build_script="nosetests", scm_repository="git://github.com/heynemann/pyoc.git", monitor_changes=True)
        repo_path = join(root_path, "tests", "functional", "repo")
        
        try:
            shutil.rmtree(repo_path)
        except:
            print "The repository folder for the test didn't exist previously. This is not an error!"
            
        service = BuildService(base_path=repo_path)
        
        build = service.build_project(project.id)

        self.failUnless(build.scm_status == ScmResult.Created or build.scm_status == ScmResult.Updated)

if __name__ == '__main__':
    unittest.main()
    

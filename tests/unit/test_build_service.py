#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from tests.base.base_unit_test import BaseUnitTest
from skink.models import Project
from skink.repositories import ProjectRepository
from skink.services import BuildService
from skink.services.executers import ShellExecuter, ExecuteResult
from skink.services.scm import GitRepository, ScmResult

class TestBuildService(BaseUnitTest):
    def test_build(self):
        project = Project("Test Project", "make test", "git_repo")
        execute_result = ExecuteResult(project.build_script, "Ran successfully", "", 0)
        scm_result = ScmResult(ScmResult.Created)

        repository_mock = self.mock.CreateMock(ProjectRepository)
        scm_mock = self.mock.CreateMock(GitRepository)
        executer_mock = self.mock.CreateMock(ShellExecuter)

        repository_mock.get(1).AndReturn(project)
        repository_mock.update(project)
        scm_mock.create_or_update(project.scm_repository).AndReturn(scm_result)
        executer_mock.execute(project.build_script).AndReturn(execute_result)
        
        self.mock.ReplayAll()
        
        service = BuildService(repository=repository_mock, scm=scm_mock, executer=executer_mock)
        
        build = service.build_project(1)
        
        self.assertEqual(build.status, BuildService.Success)
        self.mock.VerifyAll()

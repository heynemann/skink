#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)
from datetime import datetime

from tests.base.base_unit_test import BaseUnitTest
from skink.models import Project, Pipeline, PipelineItem
from skink.repositories import ProjectRepository, PipelineRepository
from skink.services import BuildService
from skink.services.executers import ShellExecuter, ExecuteResult
from skink.services.scm import GitRepository, ScmResult

class TestBuildService(BaseUnitTest):
    def do_nothing(self):
        self.done = True

    def test_build(self):
        project = Project()
        project.id = 1
        project.name = "Test Project"
        project.build_script = "make test"
        project.scm_repository = "git_repo"
        project.tabs = []

        project2 = Project()
        project.id = 2
        project2.name = "Test Project 2"
        project2.build_script = "make test"
        project2.scm_repository = "git_repo"
        project2.tabs = []
        
        execute_result = ExecuteResult(project.build_script, "Ran successfully", 0)
        scm_result = ScmResult(ScmResult.Created, "some/path/", 
        {
                   'commit_number': "1234abcd",
                   'author': "Bernardo",
                   'author_date': None,
                   'committer': "Bernardo",
                   'committer_date': None,
                   'subject': "Changed some stuff"
        }, "some log")
        
        pipeline = Pipeline()
        pipeline.items = []
        item = PipelineItem()
        item.project = project
        pipeline.items.append(item)
        item2 = PipelineItem()
        item2.project = project2
        pipeline.items.append(item)

        repository_mock = self.mock.CreateMock(ProjectRepository)
        pipeline_repository_mock = self.mock.CreateMock(PipelineRepository)
        scm_mock = self.mock.CreateMock(GitRepository)
        executer_mock = self.mock.CreateMock(ShellExecuter)

        repository_mock.get(1).AndReturn(project)
        repository_mock.update(project, None)
        scm_mock.create_or_update(project).AndReturn(scm_result)
        executer_mock.execute(project.build_script, "some/path/").AndReturn(execute_result)
        pipeline_repository_mock.get_all_pipelines_for(project).AndReturn((pipeline,))
        
        self.mock.ReplayAll()
        
        service = BuildService(repository=repository_mock, 
                               pipeline_repository=pipeline_repository_mock,
                               scm=scm_mock, 
                               executer=executer_mock)
        
        build = service.build_project(1)
        
        self.assertEqual(build.status, BuildService.Success)
        self.assertEqual(build.commit_number, "1234abcd")
        self.assertEqual(build.commit_author, "Bernardo")
        self.assertEqual(build.commit_committer, "Bernardo")
        self.assertEqual(build.commit_text, "Changed some stuff")
        
        self.mock.VerifyAll()

if __name__ == '__main__':
    unittest.main()
    

#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from tests.base.base_functional_test import BaseFunctionalTest
from skink.models import Pipeline, PipelineItem, Project
from skink.repositories import PipelineRepository, ProjectRepository

class TestPipelineRepository(BaseFunctionalTest):

    def test_create_pipeline(self):
        project_repository = ProjectRepository()

        projecta = project_repository.create(name=u"ProjectA", build_script=u"make test", scm_repository="git_repo")
        projectb = project_repository.create(name=u"ProjectB", build_script=u"make test", scm_repository="git_repo")

        repository = PipelineRepository()
        created_pipeline = repository.create(name=u"Test Pipeline", pipeline_definition="ProjectA > ProjectB")
        
        pipeline = repository.get(created_pipeline.id)
        
        self.assertEqual(pipeline.name, u"Test Pipeline")
        self.assertEqual(len(pipeline.items), 2)
        self.assertNotEqual(pipeline.items[0].project, None)
        self.assertNotEqual(pipeline.items[1].project, None)
        self.assertEqual(pipeline.items[0].project.id, projecta.id)
        self.assertEqual(pipeline.items[1].project.id, projectb.id)
        self.assertEqual(str(pipeline), "ProjectA > ProjectB")
        
    def test_get_all_pipelines(self):
        project_repository = ProjectRepository()

        projecta = project_repository.create(name=u"ProjectA", build_script=u"make test", scm_repository="git_repo")
        projectb = project_repository.create(name=u"ProjectB", build_script=u"make test", scm_repository="git_repo")
        projectc = project_repository.create(name=u"ProjectC", build_script=u"make test", scm_repository="git_repo")

        repository = PipelineRepository()
        created_pipeline = repository.create(name=u"Test Pipeline", pipeline_definition="ProjectA > ProjectB")
        created_pipeline2 = repository.create(name=u"Test Pipeline 2", pipeline_definition="ProjectB > ProjectA > ProjectC")
        
        pipelines = repository.get_all()
        
        self.assertEqual(len(pipelines), 2)
        self.assertEqual(pipelines[0].name, u"Test Pipeline")
        self.assertEqual(pipelines[1].name, u"Test Pipeline 2")
        self.assertEqual(len(pipelines[0].items), 2)
        self.assertEqual(len(pipelines[1].items), 3)

        self.assertNotEqual(pipelines[0].items[0].project, None)
        self.assertNotEqual(pipelines[0].items[1].project, None)
        self.assertEqual(pipelines[0].items[0].project.id, projecta.id)
        self.assertEqual(pipelines[0].items[1].project.id, projectb.id)
        
        self.assertNotEqual(pipelines[1].items[0].project, None)
        self.assertNotEqual(pipelines[1].items[1].project, None)
        self.assertNotEqual(pipelines[1].items[2].project, None)
        self.assertEqual(pipelines[1].items[0].project.id, projectb.id)
        self.assertEqual(pipelines[1].items[1].project.id, projecta.id)
        self.assertEqual(pipelines[1].items[2].project.id, projectc.id)
        
if __name__ == '__main__':
    unittest.main()

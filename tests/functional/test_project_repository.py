#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from elixir import session

from tests.base.base_functional_test import BaseFunctionalTest
from skink.models import Project
from skink.repositories import ProjectRepository

class TestProjectRepository(BaseFunctionalTest):

    def test_create_project(self):
        repository = ProjectRepository()
        project = repository.create(name=u"Test Project", build_script=u"make test")
        self.assertNotEqual(project.id, 0)
        self.assertEqual(project.name, u"Test Project")
        self.assertEqual(project.build_script, u"make test")
        
        projects = Project.query.all()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].id, project.id)
        self.assertEqual(projects[0].name, project.name)
        self.assertEqual(projects[0].build_script, project.build_script)

    def test_update_project(self):
        repository = ProjectRepository()
        project = repository.create(name=u"Test Project", build_script=u"make test")

        update = repository.get(project_id=project.id)
        self.assertEqual(update.id, project.id)
        self.assertEqual(update.name, project.name)
        self.assertEqual(update.build_script, project.build_script)
        
        update.name = u"Some Other Project"
        update.build_script = u"make build"
        
        repository.update(update)

        updated = repository.get(project_id=project.id)
        self.assertEqual(updated.id, project.id)
        self.assertEqual(updated.name, u"Some Other Project")
        self.assertEqual(updated.build_script, u"make build")

if __name__ == '__main__':
    unittest.main()

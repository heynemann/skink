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
    
    def test_get_project(self):
        repository = ProjectRepository()
        project = repository.create(name=u"Test Project", build_script=u"make test")

        retrieved = repository.get(project_id=project.id)
        self.assertEqual(retrieved.id, project.id)
        self.assertEqual(retrieved.name, project.name)
        self.assertEqual(retrieved.build_script, project.build_script)
        
    def test_get_all_projects(self):
        repository = ProjectRepository()
        project = repository.create(name=u"Test Project", build_script=u"make test")
        project2 = repository.create(name=u"Test Project2", build_script=u"make build")
        project3 = repository.create(name=u"Test Project3", build_script=u"make acceptance")

        projects = repository.get_all()
        
        self.assertEqual(len(projects), 3)
        self.assertEqual(projects[0].id, project.id)
        self.assertEqual(projects[0].name, project.name)
        self.assertEqual(projects[0].build_script, project.build_script)
        self.assertEqual(projects[1].id, project2.id)
        self.assertEqual(projects[1].name, project2.name)
        self.assertEqual(projects[1].build_script, project2.build_script)
        self.assertEqual(projects[2].id, project3.id)
        self.assertEqual(projects[2].name, project3.name)
        self.assertEqual(projects[2].build_script, project3.build_script)
        
if __name__ == '__main__':
    unittest.main()

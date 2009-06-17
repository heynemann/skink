#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from tests.base.base_functional_test import BaseFunctionalTest
from skink.imports import *
from skink.models import Project
from skink.repositories import ProjectRepository

class TestProjectRepository(BaseFunctionalTest):

    def test_create_project(self):
        repository = ProjectRepository()
        project = self.create_project(name=u"Test Project")

        self.assertNotEqual(project.id, 0)
        self.assertEqual(project.name, u"Test Project")
        self.assertEqual(project.build_script, u"make test")
        self.assertEqual(project.scm_repository, "git_repo")

        projects = Project.query.all()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].id, project.id)
        self.assertEqual(projects[0].name, project.name)
        self.assertEqual(projects[0].build_script, project.build_script)
        self.assertEqual(projects[0].scm_repository, project.scm_repository)

    def test_update_project(self):
        repository = ProjectRepository()
        project = self.create_project(name=u"Test Project")

        elixir.session.flush()
        elixir.session.commit()

        update = repository.get(project_id=project.id)
        self.assertEqual(update.id, project.id)
        self.assertEqual(update.name, project.name)
        self.assertEqual(update.build_script, project.build_script)

        update.name = u"Some Other Project"
        update.build_script = u"make build"
        update.scm_repository = u"new_repo"

        repository.update(update, [], [])

        elixir.session.flush()
        elixir.session.commit()

        updated = repository.get(project_id=project.id)
        self.assertEqual(updated.id, project.id)
        self.assertEqual(updated.name, u"Some Other Project")
        self.assertEqual(updated.build_script, u"make build")
        self.assertEqual(updated.scm_repository, u"new_repo")

    def test_get_project(self):
        repository = ProjectRepository()
        project = self.create_project(name=u"Test Project")

        elixir.session.flush()
        elixir.session.commit()

        retrieved = repository.get(project_id=project.id)
        self.assertEqual(retrieved.id, project.id)
        self.assertEqual(retrieved.name, project.name)
        self.assertEqual(retrieved.build_script, project.build_script)
        self.assertEqual(retrieved.scm_repository, project.scm_repository)

    def test_get_project_by_name(self):
        repository = ProjectRepository()
        project = self.create_project(name=u"Test Project")

        elixir.session.flush()
        elixir.session.commit()

        retrieved = repository.get_project_by_name(project_name="Test Project")
        self.assertEqual(retrieved.id, project.id)
        self.assertEqual(retrieved.name, project.name)
        self.assertEqual(retrieved.build_script, project.build_script)
        self.assertEqual(retrieved.scm_repository, project.scm_repository)

    def test_get_all_projects(self):
        repository = ProjectRepository()
        project = self.create_project(name=u"Test Project")
        project2 = self.create_project(name=u"Test Project2")
        project3 = self.create_project(name=u"Test Project3")

        elixir.session.flush()
        elixir.session.commit()

        projects = repository.get_all()

        self.assertEqual(len(projects), 3)
        self.assertEqual(projects[0].id, project.id)
        self.assertEqual(projects[0].name, project.name)
        self.assertEqual(projects[0].build_script, project.build_script)
        self.assertEqual(projects[0].scm_repository, project.scm_repository)
        self.assertEqual(projects[1].id, project2.id)
        self.assertEqual(projects[1].name, project2.name)
        self.assertEqual(projects[1].build_script, project2.build_script)
        self.assertEqual(projects[1].scm_repository, project2.scm_repository)
        self.assertEqual(projects[2].id, project3.id)
        self.assertEqual(projects[2].name, project3.name)
        self.assertEqual(projects[2].build_script, project3.build_script)
        self.assertEqual(projects[2].scm_repository, project3.scm_repository)

    def test_get_all_projects_as_dictionary(self):
        repository = ProjectRepository()
        project = self.create_project(name=u"Test Project")
        project2 = self.create_project(name=u"Test Project2")
        project3 = self.create_project(name=u"Test Project3")

        elixir.session.flush()
        elixir.session.commit()

        projects = repository.get_all_as_dictionary()

        self.failUnless(isinstance(projects, dict))
        self.assertEqual(len(projects.keys()), 3)
        self.assertEqual(projects["test project"].id, project.id)
        self.assertEqual(projects["test project"].name, project.name)
        self.assertEqual(projects["test project"].build_script, project.build_script)
        self.assertEqual(projects["test project"].scm_repository, project.scm_repository)
        self.assertEqual(projects["test project2"].id, project2.id)
        self.assertEqual(projects["test project2"].name, project2.name)
        self.assertEqual(projects["test project2"].build_script, project2.build_script)
        self.assertEqual(projects["test project2"].scm_repository, project2.scm_repository)
        self.assertEqual(projects["test project3"].id, project3.id)
        self.assertEqual(projects["test project3"].name, project3.name)
        self.assertEqual(projects["test project3"].build_script, project3.build_script)
        self.assertEqual(projects["test project3"].scm_repository, project3.scm_repository)

    def test_delete_project(self):
        repository = ProjectRepository()
        project = self.create_project(name=u"Test Project")

        elixir.session.flush()
        elixir.session.commit()

        repository.delete(project.id)

        elixir.session.flush()
        elixir.session.commit()

        projects = repository.get_all()

        self.assertEqual(len(projects), 0)

if __name__ == '__main__':
    unittest.main()

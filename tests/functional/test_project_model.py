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

class TestProjectModel(BaseFunctionalTest):

    def test_create_project(self):
        project = Project(name=u"Test Project", build_script=u"make test")
        session.commit()
        self.assertNotEqual(project.id, 0)
        self.assertEqual(project.name, u"Test Project")
        self.assertEqual(project.build_script, u"make test")
        
        projects = Project.query.all()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].id, project.id)
        self.assertEqual(projects[0].name, project.name)
        self.assertEqual(projects[0].build_script, project.build_script)

    def test_update_project(self):
        project = Project(name=u"Test Project", build_script=u"make test")
        session.commit()
        session.begin()
        update = Project.get_by(id=project.id)
        self.assertEqual(update.id, project.id)
        self.assertEqual(update.name, project.name)
        self.assertEqual(update.build_script, project.build_script)
        
        update.name = "Some Other Project"
        update.build_script = "make build"
        
        session.commit()
        session.begin() #TODO: REMOVE THIS AFTER SQL ALCHEMY UPGRADE

        updated = Project.get_by(id=project.id)
        self.assertEqual(updated.id, project.id)
        self.assertEqual(updated.name, "Some Other Project")
        self.assertEqual(updated.build_script, "make build")

if __name__ == '__main__':
    unittest.main()

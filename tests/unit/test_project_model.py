#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from tests.base.base_unit_test import BaseUnitTest
from skink.models import Project

class TestProjectModel(BaseUnitTest):
    def test_create_project(self):
        project = Project(name="Test Project", build_script="make test", scm_repository="git_repo")
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.build_script, "make test")
        self.assertEqual(project.scm_repository, "git_repo")

    def test_name_must_be_filled(self):
        self.assertRaises(ValueError, Project, name=None, build_script="make test", scm_repository="git_repo")
        self.assertRaises(ValueError, Project, name="", build_script="make test", scm_repository="git_repo")
        
    def test_project_build_script_must_be_filled(self):
        self.assertRaises(ValueError, Project, name="Test Project", build_script=None, scm_repository="git_repo")
        self.assertRaises(ValueError, Project, name="Test Project", build_script="", scm_repository="git_repo")

    def test_project_scm_repository_must_be_filled(self):
        self.assertRaises(ValueError, Project, name="Test Project", build_script="make test", scm_repository=None)
        self.assertRaises(ValueError, Project, name="Test Project", build_script="make test", scm_repository="")

if __name__ == '__main__':
    unittest.main()
    

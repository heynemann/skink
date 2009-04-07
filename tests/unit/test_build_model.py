#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
from datetime import datetime
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from tests.base.base_unit_test import BaseUnitTest
from skink.models import Project, Build

class TestBuildModel(BaseUnitTest):
    def test_create_build(self):
        project = Project(name="Test Project", build_script="make test", scm_repository="git_repo")
        start_date = datetime.now()
        build = Build(start_date, "SUCCESS", project)
        self.assertEqual(build.date, start_date)
        self.assertEqual(build.status, "SUCCESS")
        self.assertEqual(build.project, project)

    def test_date_must_be_filled(self):
        project = Project(name="Test Project", build_script="make test", scm_repository="git_repo")
        self.assertRaises(ValueError, Build, date=None, status="any", project=project)
        self.assertRaises(ValueError, Build, date="", status="any", project=project)
        
    def test_status_must_be_filled(self):
        project = Project(name="Test Project", build_script="make test", scm_repository="git_repo")
        start_date = datetime.now()
        self.assertRaises(ValueError, Build, date=start_date, status=None, project=project)
        self.assertRaises(ValueError, Build, date=start_date, status="", project=project)

    def test_project_must_be_filled(self):
        start_date = datetime.now()
        self.assertRaises(ValueError, Build, date=start_date, status="any", project=None)
        self.assertRaises(ValueError, Build, date=start_date, status="any", project="")

if __name__ == '__main__':
    unittest.main()
    

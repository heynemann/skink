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

class TestProjectRepository(BaseUnitTest):
    def test_create_project(self):
        session_mock = self.mock.CreateMockAnything()
        session_mock.begin()
        session_mock.commit()
        self.mock.ReplayAll()

        repository = ProjectRepository(session=session_mock)
        project = repository.create("Test Project", "make test")

        self.mock.VerifyAll()
        self.assertEqual(project.name, u"Test Project")
        self.assertEqual(project.build_script, u"make test")

if __name__ == '__main__':
    unittest.main()
    

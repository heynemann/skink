#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from tests.base.base_unit_test import BaseUnitTest
from skink.models import Project, Build

class TestProjectModel(BaseUnitTest):
    def test_get_last_build_number(self):
        project = Project()
        project.name = "Test"
        project.scm_repository = "git"
        project.build_script = "make test"
        
        self.assertEquals(project.get_last_build_number(), 0)
        
        project.builds = []
        
        build = Build()
        build.number = 1
        build.date = None
        build.status = None
        build.scm_status = None
        build.log = None
        build.project = project
    
        project.builds.append(build)
        
        self.assertEquals(project.get_last_build_number(), 1)
                
if __name__ == '__main__':
    unittest.main()
    

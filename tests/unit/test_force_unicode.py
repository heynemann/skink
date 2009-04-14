#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from tests.base.base_unit_test import BaseUnitTest
from tests.imports import *
from skink.services import *

class DoNothing():
    pass

class TestEmailPlugin(BaseUnitTest):
        
    def test_force_unicode(self):
        bs = BuildService(DoNothing(), DoNothing(), DoNothing(), DoNothing(), DoNothing())
        self.assertEqual(u"mãe", bs.force_unicode("mãe"))

if __name__ == '__main__':
    unittest.main()

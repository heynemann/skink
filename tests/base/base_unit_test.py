#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from unittest import TestCase
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

import mox

class BaseUnitTest(TestCase):

    def setUp(self):
        self.mock = mox.Mox()

    def tearDown(self):
        pass

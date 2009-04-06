#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from unittest import TestCase
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

import mox
from sqlalchemy.orm.scoping import ScopedSession
import elixir

class BaseUnitTest(TestCase):

    def setUp(self):
        self.mock = mox.Mox()
        elixir.session = self.mock.CreateMock(ScopedSession)

    def tearDown(self):
        pass

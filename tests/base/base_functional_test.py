#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from unittest import TestCase
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from elixir import *

from skink.models import metadata, setup_all, drop_all

class BaseFunctionalTest(TestCase):
    def setUp(self):
        metadata.bind = 'sqlite:///:memory:'
        setup_all()
        create_all()
        session.begin()

    def tearDown(self):
        session.close()
        drop_all()


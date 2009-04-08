#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from unittest import TestCase
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from elixir import *

from skink.models import *

class BaseFunctionalTest(TestCase):
    def setUp(self):
        metadata.bind = 'sqlite:///:memory:'
        metadata.bind.echo = True
        setup_all(create_tables=True)
        create_all()


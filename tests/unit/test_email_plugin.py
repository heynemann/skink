#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from tests.base.base_unit_test import BaseUnitTest
from skink.plugins import BasePlugin
from skink.plugins.email_plugin import EmailPlugin
from hamcrest import *
#from nope import dope

def TestEmailPlugin(BaseUnitTest):
    def do_nothing(self):
        self.done = True
        
    def test_null_configuration(self):
        assert_that(EmailPlugin(),raises(ValueError))
        self.asserRaises(ValueError,EmailPlugin())
        
        fail('Should have raised a ValueError')

if __name__ == '__main__':
    unittest.main()

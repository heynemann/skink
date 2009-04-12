#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join
import unittest
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from tests.base.base_unit_test import BaseUnitTest
from tests.imports import *
from skink.plugins import Plugin
from skink.plugins.email_plugin import EmailPlugin

class TestEmailPlugin(BaseUnitTest):
        
    def test_null_configuration(self):
        assert_that(EmailPlugin(),raises(ValueError))
        self.assertRaises(ValueError,EmailPlugin,{"enabled":True})
        fail('Should have raised a ValueError passing no smpt_host')

        self.assertRaises(ValueError,EmailPlugin,{"enabled":True, "smpt":"127.0.0.1"})
        fail('Should have raised a ValueError passing no smpt_user')


if __name__ == '__main__':
    unittest.main()

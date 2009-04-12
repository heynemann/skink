#!/usr/bin/env python
# -*- coding:utf-8 -*-

from skink.models import Project, Pipeline, PipelineItem
from skink.plugins import Plugin, Guard
from hamcrest import *

class EmailPlugin (Plugin):
    section = "EmailPlugin" 
    config_keys = ("smtp_host", "smtp_user", "smtp_passwd")
    
    def __init__(self, configuration=None):
        super(EmailPlugin, self).__init__(configuration)
        Guard.against_empty(self.configuration.get('smtp_host',None))
        Guard.against_empty(self.configuration.get('smtp_user',None))
        Guard.against_empty(self.configuration.get('smtp_passwd',None))


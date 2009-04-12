#!/usr/bin/env python
# -*- coding:utf-8 -*-

from skink.models import Project, Pipeline, PipelineItem
from skink.plugins import Plugin, Guard
from hamcrest import *

class EmailPlugin (Plugin):
    def __init__(self):
        super(EmailPlugin, self).__init__()
        Guard.against_empty(self.configuration.get('smtp_host',None))



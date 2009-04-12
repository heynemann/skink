#!/usr/bin/env python
# -*- coding:utf-8 -*-

from skink.models import Project, Pipeline, PipelineItem
from skink.plugins import Plugin, Guard

class EmailPlugin (Plugin):
    section = "EmailPlugin" 
    config_keys = ("smtp_host", "smtp_user", "smtp_pass")
    
    def __init__(self, configuration=None):
        super(EmailPlugin, self).__init__(configuration)
        self.smtp_host = self.configuration.get('smtp_host',None)
        self.smtp_user = self.configuration.get('smtp_user',None)
        self.smtp_pass = self.configuration.get('smtp_pass',None)
        Guard.against_empty(self.smtp_host)
        Guard.against_empty(self.smtp_user)
        Guard.against_empty(self.smtp_pass)


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
        Guard.against_empty(self.smtp_host,'Please provide a smpt_host parameter, so I know which server to use to send e-mails.')
        Guard.against_empty(self.smtp_user, 'Please provide a smpt_user parameter, so I know which user should I use to log on the smtp server.')
        Guard.against_empty(self.smtp_pass, 'Please provide a smpt_pass parameter, so I know which password should I use to log on the smtp server.')

    def on_project_created(self, project):
        print(" ==> on_project_created")

    def on_project_updated(self, project):
        print(" ==> on_project_updated")

    def on_project_deleted(self, project):
        print(" ==> on_project_deleted")

    def on_pipeline_created(self, pipeline):
        print(" ==> on_pipeline_created")

    def on_pipeline_updated(self, pipeline):
        print(" ==> on_pipeline_updated")

    def on_pipeline_deleted(self, pipeline):
        print(" ==> on_pipeline_deleted")

    def on_before_build(self, project):
        print(" ==> on_before_build raised")

    def on_build_successful(self, project, build):
        print(" ==> on_build_successful")

    def on_build_failed(self, project, build):
        print(" ==> on_build_failed")


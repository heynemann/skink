#!/usr/bin/env python
# -*- coding:utf-8 -*-

from skink.models import Project, Pipeline, PipelineItem
from skink.plugins import Plugin, Guard
import smtplib

class EmailPlugin (Plugin):
    section = "EmailPlugin" 
    config_keys = ("smtp_host", "smtp_user", "smtp_pass")
    
    def __init__(self, configuration=None):
        super(EmailPlugin, self).__init__(configuration)

        self.enabled = self.configuration["enabled"]
        Guard.against_empty(self.enabled,'Please provide an "enabled" parameter, so I know if I should raise events.')
        
        if not self.enabled:
            return

        self.smtp_host = self.configuration.get('smtp_host',None)
        self.smtp_user = self.configuration.get('smtp_user',None)
        self.smtp_pass = self.configuration.get('smtp_pass',None)
        self.email_sender = self.configuration.get('email_sender',None)
        self.email_recipients = self.configuration.get('email_recipients',None)

        Guard.against_empty(self.smtp_host,'Please provide a smpt_host parameter, so I know which server to use to send e-mails.')
        Guard.against_empty(self.smtp_user, 'Please provide a smpt_user parameter, so I know which user should I use to log on the smtp server.')
        Guard.against_empty(self.smtp_pass, 'Please provide a smpt_pass parameter, so I know which password should I use to log on the smtp server.')
        Guard.against_empty(self.email_sender, 'Please provide an email_sender parameter, so I know how to inform who sent the e-mail.')
        Guard.against_empty(self.email_recipients, 'Please provide an email_recipients parameter, so I know whom I have to send the e-mail.')
        
        self.__smpt_session = self.__create_smtp_session__(self.smtp_host,self.smtp_user,self.smtp_pass)
        
    def __create_smtp_session__(self,host,user,password):
          session = smtplib.SMTP(host)
          session.login(user, password)
          return session

    def __send_email__(self, msg):
        smtpresult = session.sendmail(self.email_sender, self.email_recipients, msg)
        if smtpresult:
            errstr = ""
            for recip in smtpresult.keys():
                errstr = """Could not delivery mail to: %s

                Server said: %s
                %s
                
                %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
            raise smtplib.SMTPException, errstr

    def on_project_created(self, project):
        print(" ==> on_project_created")
        self.__send_email__("project [%s]created " % project.name)

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


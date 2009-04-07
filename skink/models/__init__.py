#!/usr/bin/env python
#-*- coding:utf-8 -*-

from elixir import *

class ModelHelper(object):
    @classmethod
    def assert_not_empty(self, message, **arguments):
        return_message = []
        for argument, value in arguments.items():
            if value is None or value == "":
                return_message.append(message % argument)
        if return_message:
            raise ValueError("The following errors happened:\n%s" % "\n".join(return_message))

class Project(Entity):
    name = Field(Unicode(255))
    build_script = Field(Unicode(2000))
    scm_repository = Field(Unicode(1500))
    last_build_number = Field(Integer)
    builds = OneToMany('Build')
    using_options(tablename="projects")
    
    def __init__(self, name, build_script, scm_repository):
        super(Project, self).__init__()
        ModelHelper.assert_not_empty("The field %s of the Project model must not be empty or null.", name=name, build_script=build_script, scm_repository=scm_repository)
        self.name = name
        self.build_script = build_script
        self.scm_repository = scm_repository
        self.last_build_number = 0
        
    def get_build_by_id(self, build_id):
        for build in self.builds:
            if build.id == build_id:
                return build
        return None

class Build(Entity):
    number = Field(Integer)
    date = Field(DateTime)
    status = Field(Unicode(20))
    scm_status = Field(Unicode(20))
    log = Field(Unicode(4000))
    project = ManyToOne('Project')
    using_options(tablename="builds")
    
    def __init__(self, date, status, scm_status, log, project):
        super(Build, self).__init__()
        ModelHelper.assert_not_empty("The field %s of the Build model must not be empty or null.", date=date, status=status, project=project)
        self.date = date
        self.status = status
        self.project = project
        self.scm_status = scm_status
        self.log = log
        self.number = 0

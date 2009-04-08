#!/usr/bin/env python
#-*- coding:utf-8 -*-

from elixir import *

class Project(Entity):
    name = Field(Unicode(255))
    build_script = Field(Unicode(2000))
    scm_repository = Field(Unicode(1500))
    builds = OneToMany('Build', order_by="-date")
    using_options(tablename="projects")
            
    def get_build_by_id(self, build_id):
        for build in self.builds:
            if build.id == build_id:
                return build
        return None
    
    def get_last_build_number(self):
        if not hasattr(self, 'builds') or not self.builds:
            return 0
        return len(self.builds)

    def get_status(self):
        if not hasattr(self, 'builds') or not self.builds:
            return "UNKNOWN"
        return self.builds[0].status
    
    def get_last_successful_build(self):
        if not hasattr(self, 'builds') or not self.builds:
            return "UNKNOWN"
        for build in self.builds:
            if build.status=="SUCCESS":
                return "#%s (%s)" % (build.number, build.date.strftime("%m/%d/%Y %H:%M:%S"))

        return "NONE"

class Build(Entity):
    number = Field(Integer)
    date = Field(DateTime)
    status = Field(Unicode(20))
    scm_status = Field(Unicode(20))
    log = Field(Unicode(4000))
    project = ManyToOne('Project')
    using_options(tablename="builds")


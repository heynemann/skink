#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

import elixir

from skink.models import Project

class BaseRepository(object):
    def __init__(self, session=elixir.session):
        self.session = session

class ProjectRepository(BaseRepository):
    def create(self, name, build_script):
        '''Creates a new project.'''
        self.session.begin()
        project = Project(name=name, build_script=build_script)
        self.session.commit()
        
        return project

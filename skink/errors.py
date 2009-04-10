#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../"))
sys.path.insert(0, root_path)

class ProjectNotFoundError(ValueError):
    def __init__(self, message):
        super(ProjectNotFoundError, self).__init__(message)


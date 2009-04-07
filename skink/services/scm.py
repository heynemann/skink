#!/usr/bin/env python
# -*- coding:utf-8 -*-

class GitRepository(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def create_or_update(self, repository):
        pass
        
class ScmResult(object):
    Created = "CREATED"
    Updated = "UPDATED"
    Failed = "FAILED"
    
    def __init__(self, status):
        self.status = status

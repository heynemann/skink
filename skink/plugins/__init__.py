#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from ConfigParser import ConfigParser
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../"))
sys.path.insert(0, root_path)

class Plugin (object):
    def __init__(self):
        self.configuration = {}
        if hasattr(self, "ignore_configuration"):
            if getattr(self, "ignore_configuration"):
                return;
        
        if not hasattr(self, "section") or not hasattr(self,"config_keys"):
            raise "The plugin %s failed to provide a section (using 'section' class attribute) and a configurations collection (using a tuple in 'config_keys' class attribute. If your plugin does not need any configurations please add a class attribute of ignore_configuration=True to your plugin class."

        config = ConfigParser()
        config.read(join(root_path, "config.ini"))
        for key in self.config_keys:
            self.configuration[key] = config.get(self.section, key)

    def OnProjectCreated(self, project):
        pass

    def OnProjectUpdated(self, project):
        pass

    def OnProjectDeleted(self, project):
        pass

    def OnPipelineCreated(self, pipeline):
        pass

    def OnPipelineUpdated(self, pipeline):
        pass

    def OnPipelineDeleted(self, pipeline):
        pass

    def OnBeforeBuild(self, project):
        pass

    def OnBuildSuccessful(self, project, build):
        pass

    def OnBuildFailed(self, project, build):
        pass
        
class Guard (object):

    def against_empty(obj, error_message=None):
        if not error_message:
            error_message = 'None receive when some value was expected.'
        raise ValueError(error_message)

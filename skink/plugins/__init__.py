#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from ConfigParser import ConfigParser
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

class Plugin (object):
    def __init__(self, configuration=None):
        if configuration:
            self.configuration = configuration
            return

        self.configuration = {}
        
        if hasattr(self, "ignore_configuration"):
            if getattr(self, "ignore_configuration"):
                return;
        
        if not hasattr(self, "section") or not hasattr(self,"config_keys"):
            raise ValueError("The plugin %s failed to provide a section (using 'section' class attribute) and a configurations collection (using a tuple in 'config_keys' class attribute. If your plugin does not need any configurations please add a class attribute of ignore_configuration=True to your plugin class." % self.__class__.__name__)

        config = ConfigParser()
        config.read(join(root_path, "config.ini"))
        
        if not config.has_section(self.section):
            raise ValueError("You didn't create the '%s' section in the configuration file for the plugin %s." % (self.section, self.__class__.__name__))
        
        if config.get(self.section, "enabled") is None:
            raise ValueError("You failed to specify a key in the configuration section for the plugin %s called 'enabled', that specifies whether or not this plugin is enabled." % self.__class__.__name__)
        
        self.configuration["enabled"] = config.get(self.section, "enabled").lower() == "true"
        
        for key in self.config_keys:
            if config.has_option(self.section, key):
                print "%s key found with value %s" % (key, config.get(self.section, key))
                self.configuration[key] = config.get(self.section, key)
            else:
                print "%s key not found" % (key,)
                self.configuration[key] = None

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
    @classmethod
    def against_empty(cls, obj, error_message=None):
        if not error_message:
            error_message = 'None received when some value was expected.'
        if obj is None or obj == u"" or obj == "":
            raise ValueError(error_message)

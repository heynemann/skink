#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from ConfigParser import ConfigParser
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.context import SkinkContext

class PluginEvents(object):

    @classmethod
    def raiseEvent(cls, event, *args, **kwargs):
        for plugin in SkinkContext.current().plugins:
            if hasattr(plugin, event):
                method = getattr(plugin, event)
                method(*args, **kwargs)

    @classmethod
    def on_project_created(cls, project):
        cls.raiseEvent("on_project_created", project=project)

    @classmethod
    def on_project_updated(cls, project):
        cls.raiseEvent("on_project_updated", project=project)

    @classmethod
    def on_project_deleted(cls, project):
        cls.raiseEvent("on_project_deleted", project=project)

    @classmethod
    def on_pipeline_created(cls, pipeline):
        cls.raiseEvent("on_pipeline_created", pipeline=pipeline)

    @classmethod
    def on_pipeline_updated(cls, pipeline):
        cls.raiseEvent("on_pipeline_updated", pipeline=pipeline)

    @classmethod
    def on_pipeline_deleted(cls, pipeline):
        cls.raiseEvent("on_pipeline_deleted", pipeline=pipeline)

    @classmethod
    def on_before_build(cls, project):
        cls.raiseEvent("on_before_build", project=project)

    @classmethod
    def on_build_successful(cls, project, build):
        cls.raiseEvent("on_build_successful", project=project, build=build)

    @classmethod
    def on_build_failed(cls, project, build):
        cls.raiseEvent("on_build_failed", project=project, build=build)

class Plugin (object):
    def __init__(self, configuration=None):
        #import pdb; pdb.set_trace()

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
        self.enabled = self.configuration["enabled"]
        
        for key in self.config_keys:
            if config.has_option(self.section, key):
                #print "%s key found with value %s" % (key, config.get(self.section, key))
                self.configuration[key] = config.get(self.section, key)
            else:
                #print "%s key not found" % (key,)
                self.configuration[key] = None

    def __display_not_overriden(self, event_name):
        print "%s raised and not overriden for %s" % (event_name, self.__class__.__name__)

    def on_project_created(self, project):
        self.__display_not_overriden("on_project_created")

    def on_project_updated(self, project):
        self.__display_not_overriden("on_project_updated")

    def on_project_deleted(self, project):
        self.__display_not_overriden("on_project_deleted")

    def on_pipeline_created(self, pipeline):
        self.__display_not_overriden("on_pipeline_created")

    def on_pipeline_updated(self, pipeline):
        self.__display_not_overriden("on_pipeline_updated")

    def on_pipeline_deleted(self, pipeline):
        self.__display_not_overriden("on_pipeline_deleted")

    def on_before_build(self, project):
        self.__display_not_overriden("on_before_build raised")

    def on_build_successful(self, project, build):
        self.__display_not_overriden("on_build_successful")

    def on_build_failed(self, project, build):
        self.__display_not_overriden("on_build_failed")
        
class Guard (object):
    @classmethod
    def against_empty(cls, obj, error_message=None):
        if not error_message:
            error_message = 'None received when some value was expected.'
        if obj is None or obj == u"" or obj == "":
            raise ValueError(error_message)

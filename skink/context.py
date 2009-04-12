#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from ConfigParser import ConfigParser
import Queue
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../"))
sys.path.insert(0, root_path)

from skink.imports import *
from skink.plugins import Plugin

class SkinkContext:
    instance = None
    @classmethod
    def current(cls):
        if not cls.instance:
            cls.instance = cls()
            config = ConfigParser()
            config.read(join(root_path, "config.ini"))
            cls.instance.current_template = config.get("General", "current_template")
            cls.instance.build_path = config.get("General", "build_path")
            cls.instance.host = config.get("General", "host")
            cls.instance.port = int(config.get("General", "port"))
            cls.instance.username = config.get("General", "username")
            cls.instance.password = config.get("General", "password")
            cls.instance.worker_processes = int(config.get("General", "worker_processes"))
            cls.instance.keep_polling = True
            cls.instance.build_queue = Queue.deque()
            cls.instance.projects_being_built = Queue.deque()
            cls.instance.polling_interval = int(config.get("SCM", "polling_interval"))
            cls.instance.scm_verbose = config.get("SCM", "scm_verbose") == "True"
            cls.instance.build_verbose = config.get("General", "build_verbose") == "True"
            cls.instance.webserver_verbose = config.get("General", "webserver_verbose") == "True"
            cls.instance.db_verbose = config.get("Database", "db_verbose") == "True"
            cls.instance.db_connection = config.get("Database", "db_connection")

            cls.instance.plugin_path = config.get("General", "plugin_path")
            
            IoC.reset()
            config = InPlaceConfig()
            
            config.register("configuration", None)
            config.register_files("plugins", join(root_path, "skink", cls.instance.plugin_path), "*_plugin.py")
            
            IoC.configure(config)
            
            cls.instance.plugins = [plugin for plugin in IoC.resolve_all("plugins") if plugin.enabled]
            print "%d enabled plugins found: %s" % (len(cls.instance.plugins), ", ".join([klass.__class__.__name__ for klass in cls.instance.plugins]))
            
        return cls.instance

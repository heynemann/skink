#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import Queue
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../"))
sys.path.insert(0, root_path)
from ConfigParser import ConfigParser

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
            cls.instance.worker_processes = int(config.get("General", "worker_processes"))
            cls.instance.keep_polling = True
            cls.instance.build_queue = Queue.deque()
        
        return cls.instance

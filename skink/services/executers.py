#!/usr/bin/env python
# -*- coding:utf-8 -*-

class ShellExecuter(object):
    def __init__(self, base_path):
        self.base_path = base_path
    
    def execute(self, build_script):
        pass
    
class ExecuteResult(object):
    def __init__(self, command, run_log, error_log, exit_code):
        self.command = command
        self.run_log = run_log
        self.error_log = error_log
        self.exit_code = exit_code

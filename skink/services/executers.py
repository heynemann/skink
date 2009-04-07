#!/usr/bin/env python
# -*- coding:utf-8 -*-

import commands

class ShellExecuter(object):
    def execute(self, command, base_path, change_dir=True):
        complement=""
        if change_dir:
            complement = "cd %s && " % base_path
        
        result = commands.getstatusoutput("%s%s" % (complement, command))
        return ExecuteResult(command, result[1], result[0])

class ExecuteResult(object):
    def __init__(self, command, run_log, exit_code):
        self.command = command
        self.run_log = run_log
        self.exit_code = exit_code

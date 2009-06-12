#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from subprocess import Popen, PIPE

class ShellExecuter(object):
    def execute(self, command, base_path, change_dir=True):
        print ("Executing command: %s" % command)

        try:
            if os.name == "nt":
                proc = Popen(command, stdout=PIPE, stderr=PIPE, cwd=base_path, shell=True)
            else:
                proc = Popen(command, stdout=PIPE, stderr=PIPE, cwd=base_path)
                
            log = "\n".join(proc.communicate())
            exit_code = proc.returncode

            return ExecuteResult(command, log, exit_code)
        except Exception, err:
            error_message = "An error occured while executing command %s: %s" % (command, err)
            return ExecuteResult(command, error_message, 1)

class ExecuteResult(object):
    def __init__(self, command, run_log, exit_code):
        self.command = command
        self.run_log = run_log
        self.exit_code = exit_code

#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from subprocess import Popen, PIPE

class ShellExecuter(object):
    def execute(self, command, base_path, change_dir=True):
        print ("Executing command: %s" % command)
        complement=""
        arguments = os.name == "nt" and command.split(" ") or [command]

        try:
            proc = Popen(command.split(" "), stdout=PIPE, stderr=PIPE, cwd=base_path)
            log = "\n".join(proc.communicate())
            exit_code = proc.returncode
        except Exception, err:
            return ExecuteResult(command, "An error occured while executing command %s: %s" % (command, err), 1)
        return ExecuteResult(command, log, exit_code)

class ExecuteResult(object):
    def __init__(self, command, run_log, exit_code):
        self.command = command
        self.run_log = run_log
        self.exit_code = exit_code

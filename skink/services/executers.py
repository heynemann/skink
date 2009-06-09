#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from subprocess import Popen, PIPE

class ShellExecuter(object):
    def execute(self, command, base_path, change_dir=True):
        print ("Executing command: %s" % command)
        complement=""
        if change_dir:
            oldpath = os.path.abspath(os.curdir)
            if os.path.exists(base_path):
                os.chdir(base_path)

        arguments = os.name == "nt" and command.split(" ") or [command]

        proc = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
        log = "\n".join(proc.communicate())
        exit_code = proc.returncode
        if change_dir:
            os.chdir(oldpath)
        return ExecuteResult(command, log, exit_code)

class ExecuteResult(object):
    def __init__(self, command, run_log, exit_code):
        self.command = command
        self.run_log = run_log
        self.exit_code = exit_code

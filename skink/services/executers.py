#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import time
from subprocess import Popen, PIPE
import popen2
import commands

class ShellExecuter(object):
    def execute(self, command, base_path, change_dir=True):
        print ("Executing command: %s" % command)

        try:
            if os.name == "nt":
                proc = Popen(command, stdout=PIPE, stderr=PIPE, cwd=base_path, shell=True)
                log = "\n".join(proc.communicate())
                exit_code = proc.returncode
            else:
                complement=""
                if change_dir:
                    complement = "cd %s && " % base_path
                #result = commands.getstatusoutput("%s%s" % (complement, command))
                #log = result[1]
                #exit_code = result[0]
                fd = popen2.Popen4('%s%s' % (complement, command))
                exit_code = fd.poll()
                while exit_code == -1:
                    time.sleep(0.5)
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    exit_code = fd.poll()
                log = fd.fromchild.read()

            return ExecuteResult(command, log, exit_code)
        except Exception, err:
            error_message = "An error occured while executing command %s: %s" % (command, err)
            return ExecuteResult(command, error_message, 1)

class ExecuteResult(object):
    def __init__(self, command, run_log, exit_code):
        self.command = command
        self.run_log = run_log
        self.exit_code = exit_code

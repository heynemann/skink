#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import time
from subprocess import Popen, PIPE
import popen2
import commands

class ShellExecuter(object):
    def ellapsed(self, start_time=None, end_time=None):
        '''The number of milliseconds that this story took to run.'''
        if start_time is None:
            return 0

        if end_time is None:
            return time.time() - start_time

        return end_time - start_time

    def execute(self, command, base_path, change_dir=True, timeout=None):
        try:
            start_time = time.time()
            if os.name == "nt":
                proc = Popen(command, stdout=PIPE, stderr=PIPE, cwd=base_path, shell=True)
                log = "\n".join(proc.communicate())
                exit_code = proc.returncode
            else:
                complement=""
                if change_dir:
                    complement = "cd %s && " % base_path

                fd = popen2.Popen4('%s%s' % (complement, command))
                exit_code = fd.poll()
                while exit_code == -1:
                    time.sleep(0.5)
                    print "[%s] - %.2f secs" % (command, self.ellapsed(start_time=start_time)) 
                    exit_code = fd.poll()
                    if timeout and self.ellapsed(start_time=start_time) > timeout:
                        os.kill(fd.pid, 9)
                        error_message = "\nThe build timed out after %d seconds!!! \n\nLOG: \n%s" % (timeout, fd.fromchild.read())
                        return ExecuteResult(command, error_message, 1)
                log = fd.fromchild.read()
                print "[%s] - Finished after %.2f secs" % (command, self.ellapsed(start_time=start_time)) 

            return ExecuteResult(command, log, exit_code)
        except Exception, err:
            error_message = "An error occured while executing command %s: %s" % (command, err)
            return ExecuteResult(command, error_message, 1)

class ExecuteResult(object):
    def __init__(self, command, run_log, exit_code):
        self.command = command
        self.run_log = run_log
        self.exit_code = exit_code

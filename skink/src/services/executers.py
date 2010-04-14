#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import time

import skink.lib
from cleese import Executer, Status
import cherrypy

class ShellExecuter(object):
    def __init__(self, verbose=False):
        self.start_execute = None
        self.finish_execute = None
        self.execute_beat = None
        self.timed_out = None
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            cherrypy.log(message, '[SHELLEXECUTER]')

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

            self.executer = Executer(command=command, working_dir=base_path)

            if self.start_execute:
                self.start_execute(executer=self.executer)
            self.executer.execute()

            while not self.executer.poll():
                if self.execute_beat:
                    self.execute_beat(executer=self.executer)

                time.sleep(1)
                self.log("[%s] - %.2f secs" % (command, self.ellapsed(start_time=start_time)))

                if timeout and self.ellapsed(start_time=start_time) > timeout:
                    self.executer.process.stop()
                    if self.timed_out:
                        self.timed_out(executer=self.executer)

                    error_message = "\nThe build timed out after %d seconds!!! \n\nLOG: \n%s" % (timeout, self.executer.result.log)
                    return ExecuteResult(command, error_message, 1)

            log = self.executer.result.log
            if self.finish_execute:
                self.finish_execute(executer=self.executer)

            self.log("[%s] - Finished after %.2f secs" % (command, self.ellapsed(start_time=start_time)))

            return ExecuteResult(command, log, self.executer.result.exit_code)
        except Exception, err:
            error_message = "An error occured while executing command %s: %s" % (command, err)
            return ExecuteResult(command, error_message, 1)

class ExecuteResult(object):
    def __init__(self, command, run_log, exit_code):
        self.command = command
        self.run_log = run_log
        self.exit_code = exit_code

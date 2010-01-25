#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright Bernardo Heynemann <heynemann@gmail.com>

# Licensed under the Open Software License ("OSL") v. 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.opensource.org/licenses/osl-3.0.php

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import os
from cleese.subprocess import Popen, PIPE, STDOUT

from cleese import Status

class Executer(object):
    def __init__(self, command, working_dir=None):
        self.command = command
        self.working_dir = working_dir
    
    def execute(self):
        self.result = ExecuteResult(command=self.command)
        self.result.status = Status.running
        self.process = Process (self.command, self.working_dir)
        self.process.start()
    
    def poll(self):
        exit_code = self.process.poll()
        self.result.log += self.process.read_log()

        if exit_code is None:
            return False

        if int(exit_code) > 0:
            self.result.status = Status.fail

        if int(exit_code) == 0:
            self.result.status = Status.success

        self.result.exit_code = exit_code
        last_log = self.process.process.communicate()[0]
        self.result.log = last_log and last_log or self.result.log
        return exit_code is not None

class Process(object):
    def __init__(self, command, working_dir, buffer_size=1):
        self.command = command
        self.buffer_size = buffer_size
        self.working_dir = working_dir

    def poll(self):
        if not self.process:
            return 0

        return self.process.poll()

    def start(self):
        self.process = Popen(str(self.command), cwd=self.working_dir, shell=True, stdout=PIPE, stderr=STDOUT)

    def stop(self):
        pid = self.process.pid
        os.kill(pid, 9)

    def read_log(self):
        return self.process.asyncread()

class ExecuteResult(object):
    def __init__(self, command):
        self.command = command
        self.status = Status.unknown
        self.log = ''


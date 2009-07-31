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
from subprocess import PIPE, STDOUT
from popen import Popen, recv_some

from cleese import Status

class Executer(object):
    def __init__(self, command, working_dir=None):
        self.command = command
        self.working_dir = working_dir
    
    def execute(self):
        self.result = ExecuteResult(command=self.command)
        self.result.status = Status.running
        self.process = Popen (self.command, cwd=self.working_dir, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    
    def poll(self):
        exit_code = self.process.poll()
        self.result.log += recv_some(self.process, e=0)

        if exit_code is None:
            return False
        
        if int(exit_code) > 0:
            self.result.status = Status.fail

        if int(exit_code) == 0:
            self.result.status = Status.success

        self.result.exit_code = exit_code
        last_log = self.process.communicate()[0]
        self.result.log = last_log and last_log or self.result.log
        return exit_code is not None

class ExecuteResult(object):
    def __init__(self, command):
        self.command = command
        self.status = Status.unknown
        self.log = ''


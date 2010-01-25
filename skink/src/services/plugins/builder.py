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

#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import time
from threading import Thread

from os.path import dirname, abspath, join, exists

import skink.lib
from ion.plugins import CherryPyDaemonPlugin

class BuilderPlugin(CherryPyDaemonPlugin):
    key = "BUILDER"

    def execute(self):
        ctx = self.server.context
        if ctx.build_queue:
            item = ctx.build_queue.pop()
            self.do_log("Found %s to build. Building..." % item)
            #self.build_service.build_project(item)
            self.do_log("Project %s finished building." % item)
        else:
            self.do_log("No Projects found to build!")
        time.sleep(int(ctx.settings.Skink.build_polling_interval))


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

import sys
import os
from os.path import join, dirname, abspath, exists
from string import Template

from ion.server import Server
from ion.fs import *
from ion import Version

def log(message):
    print message

__PROVIDERS__ = []
__PROVIDERSDICT__ = {}

class MetaProvider(type):
    def __init__(cls, name, bases, attrs):
        if name not in ('MetaProvider', 'Provider'):
            __PROVIDERS__.append(cls)
            __PROVIDERSDICT__[name] = cls

        super(MetaProvider, cls).__init__(name, bases, attrs)

class Provider(object):
    __metaclass__ = MetaProvider

    @classmethod
    def all(self):
        return __PROVIDERS__

    def __init__(self, key):
        self.key = key

class VersionProvider(Provider):
    def __init__(self):
        super(VersionProvider, self).__init__("version")

    def execute(self, current_dir, options, args):
        log("Ion v%s - http://github.com/heynemann/ion\nCreated by Bernardo Heynemann (heynemann@gmail.com)" % Version)

class HelpProvider(Provider):
    def __init__(self):
        super(HelpProvider, self).__init__("help")

    def execute(self, current_dir, options, args):
        log("Help to be written")

class CreateProjectProvider(Provider):
    def __init__(self):
        super(CreateProjectProvider, self).__init__("create")

    def replace_tokens(self, path, **kw):
        for file_name in locate("*.txt", "*.py", "*.css", "*.js", "*.rst", "*.html", "*.ini", root=path):
            if not is_file(file_name):
                continue
            text = read_all_file(file_name)

            remove_file(file_name)

            s = Template(text)

            contents = s.substitute(**kw)
            replace_file_contents(file_name, contents)

    def execute(self, current_dir, options, args):
        if not args or not args[0]:
            raise ValueError("You need to pass the project name to be created")

        project_name = args[0]

        new_project_template = abspath(join(dirname(__file__), "new_project"))
        to_project_path = abspath(join(current_dir, project_name))

        if exists(to_project_path):
            raise ValueError("The choosen path(%s) already exists! Please choose a different name or try another folder." % to_project_path)

        recursive_copy(new_project_template, to_project_path)

        self.replace_tokens(to_project_path, project_name=project_name)

        move_dir(join(to_project_path, "src"), join(to_project_path, project_name))

class RunServerProvider(Provider):
    def __init__(self):
        super(RunServerProvider, self).__init__("run")

    def execute(self, current_dir, options, args):
        ini_files = locate("config.ini", root=current_dir)

        if not ini_files:
            raise RuntimeError("No files called config.ini were found in the current directory structure")

        root_dir = abspath(dirname(ini_files[0]))

        sys.path.append(os.curdir)
        sys.path.append(root_dir)

        server = Server(root_dir=root_dir)

        try:
            server.start("config.ini")
        except KeyboardInterrupt:
            server.stop()

class TestRunnerProvider(Provider):
    def __init__(self, key=None):
        super(TestRunnerProvider, self).__init__(key or "test")

    def run_nose(self, path, project_name):
        from nose.core import run
        from nose.config import Config

        argv = ["-d", "-s", "--verbose"]

        if exists(join(path, 'nose.cfg')):
            argv.append("--config=%s" % (join(path, 'nose.cfg')))

        use_coverage = True
        try:
            import coverage
            argv.append("--with-coverage")
            argv.append("--cover-erase")
            #argv.append("--cover-package=%s" % project_name)
            argv.append("--cover-inclusive")
        except ImportError:
            pass

        argv.append(path)

        result = run(argv=argv)
        if not result:
            sys.exit(1)

    def execute(self, current_dir, options, args):
        tests_dir = join(current_dir, "tests")
        self.run_nose(tests_dir, os.path.split(current_dir)[-1])

class UnitTestProvider(TestRunnerProvider):
    def __init__(self):
        super(UnitTestProvider, self).__init__("unit")

    def execute(self, current_dir, options, args):
        tests_dir = join(current_dir, "tests", "unit")
        self.run_nose(tests_dir, os.path.split(current_dir)[-1])

class FunctionalTestProvider(TestRunnerProvider):
    def __init__(self):
        super(FunctionalTestProvider, self).__init__("func")

    def execute(self, current_dir, options, args):
        tests_dir = join(current_dir, "tests", "functional")
        self.run_nose(tests_dir, os.path.split(current_dir)[-1])


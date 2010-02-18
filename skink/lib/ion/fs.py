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

import os
from os.path import join, dirname, abspath, exists, isfile
from os import walk, remove

import fnmatch
import shutil

open_file = open

#should be called like: locate('*.txt', '*.py', '*.acc', root=path)
def locate(*args, **kw):
    root = 'root' in kw and kw['root'] or os.curdir
    root_path = abspath(root)
    patterns = args

    return_files = []
    for path, dirs, files in walk(root_path):
        for pattern in args:
            for filename in fnmatch.filter(files, pattern):
                return_files.append(join(path, filename))
    return return_files

def recursive_copy(from_path, to_path):
    shutil.copytree(from_path, to_path)

def move_dir(from_path, to_path):
    shutil.move(from_path, to_path)

def read_all_file(path):
    project_file = open_file(path, 'r')
    text = project_file.read()
    project_file.close()

    return text

def replace_file_contents(path, contents):
    project_file = open_file(path, 'w')
    project_file.write(contents)
    project_file.close()

def remove_file(path):
    remove(path)

def is_file(path):
    return isfile(path)


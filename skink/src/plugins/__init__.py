#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from os.path import split, splitext, join, dirname, abspath
from glob import glob

root_path = abspath(dirname(__file__))

sys.path.append(root_path)

for pyfile in glob(join(root_path, "*.py")):
    module = splitext(split(pyfile)[-1])[0]
    if module.lower() == 'base':
        continue
    __import__(module)

sys.path.remove(root_path)
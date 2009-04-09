#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../"))
sys.path.insert(0, root_path)

lib_path = join(root_path, "skink", "lib")
sys.path.insert(0, lib_path)

#mox - For mock unit tests
import mox

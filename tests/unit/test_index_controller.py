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

from fudge import Fake, with_fakes, with_patched_object, clear_expectations
from fudge.inspector import arg

from skink.src.controllers.index_controller import IndexController

import skink.lib
import ion.controllers as ctrl

def clear():
    ctrl.__CONTROLLERS__ = []
    ctrl.__CONTROLLERSDICT__ = {}

custom_render_template = Fake(callable=True).with_args('index.html').returns('Some Result')

@with_fakes
@with_patched_object(IndexController, "render_template", custom_render_template)
def test_index_action():
    clear()
    ctrl = IndexController()
    result = ctrl.index()

    assert result == "Some Result"

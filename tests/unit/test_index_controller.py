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

import skink.src.controllers.index_controller as index_ctrl

import skink.lib
import ion.controllers as ctrl

from skink.src.models import *

def clear():
    ctrl.__CONTROLLERS__ = []
    ctrl.__CONTROLLERSDICT__ = {}

fake_store = Fake("store")

custom_render_template = Fake(callable=True).with_args('index.html', projects=[0, 1, 2]).returns('Some Result')

@with_patched_object(index_ctrl.IndexController, "render_template", custom_render_template)
@with_patched_object(index_ctrl.IndexController, "store", fake_store)
@with_fakes
def test_index_action():
    clear()
    clear_expectations()

    index_ctrl.IndexController.store.expects("find").with_args(Project).returns([0, 1, 2])

    controller = index_ctrl.IndexController()
    result = controller.index()

    assert result == "Some Result"


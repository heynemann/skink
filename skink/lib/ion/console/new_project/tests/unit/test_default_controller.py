#!/usr/bin/env python
#-*- coding:utf-8 -*-

from $project_name.controllers import *

def fake_render_template(self, template, *args, **kw):
    return "fake rendered text args: %s kw: %s" % (args, kw)

DefaultController.render_template = fake_render_template

def test_default_controller_index_action():
    ctrl = DefaultController()

    result = ctrl.index()
    assert "date" in result
    assert "fake rendered text" in result

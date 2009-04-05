#!/usr/bin/env python
#-*- coding:utf-8 -*-

class ModelHelper(object):
    @classmethod
    def assert_not_empty(self, message, **arguments):
        return_message = []
        for argument, value in arguments.items():
            if value is None or value == "":
                return_message.append(message % argument)
        if return_message:
            raise ValueError("The following errors happened:\n%s" % "\n".join(return_message))

class Project (object):
    def __init__(self, name, build_script):
        ModelHelper.assert_not_empty("The field %s of the Project model must not be empty or null.", name=name, build_script=build_script)
        self.name = name
        self.build_script = build_script

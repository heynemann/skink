#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.imports import *
from skink.context import SkinkContext

def authenticated(**options):
    """Decorator that identifies whether a user is authenticated and if not redirects him to the login page."""
    def decorate(func):
        def wrapper(*args, **kwargs):
            if not cherrypy.session.get('authenticated'):
                raise cherrypy.HTTPRedirect('/loginerror')
            return_value = func(*args, **kwargs)
            return return_value
        return wrapper
    return decorate

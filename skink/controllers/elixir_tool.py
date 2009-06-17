#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
elixir_tool.py

Usage:
from skink.controllers.elixir_tool import metadata, session, mapper
# Use the above metadata, session, mapper when defining your models

In your application configuration:

[/]
tools.ElixirTransaction.on = True
tools.ElixirTransaction.dburi = 'sqlite:///database.sqlite'
tools.ElixirTransaction.echo = False           # this is the default
tools.ElixirTransaction.convert_unicode = True # this is the default

If you set *echo* to True, SQLAlchemy will print the SQL statements.

*convert_unicode* should always be True and you should always
use unicode strings with SQLAlchemy!

When you are at the interpreter you can do:

    from skink.controllers.elixir_tool import configure_session_for_app
    configure_session_for_app(your_cherrypy_app)
'''

import sys
from sys import exc_info
import os

from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.imports import *

def configure_session():
    pass

class ElixirTransaction(cherrypy.Tool):
    passable_exceptions=[cherrypy.HTTPRedirect] # KeyboardInterrupt, SystemExit

    def __init__(self):
        self._name = 'ElixirTransaction'
        self._point = 'on_start_resource'
        self.callable = configure_session
        self._priority = 50
        # If this priority is not appropriate for both hook points, know that
        # you can set a 'priority' attribute on the actual functions.
        # Tool.priority is just a shortcut for that.
    
    def _setup(self):
        if request.config.get('tools.staticdir.on', False) or \
            request.config.get('tools.staticfile.on', False):
                return
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('on_end_resource', self.on_end_resource)
    
    def on_end_resource(self):
        if "buildstatus" in request.path_info:
            return

        typ, value, trace = exc_info()

        if value is not None and not typ in self.passable_exceptions:
            elixir.session.rollback()
            return
        try:
            elixir.session.flush()
            elixir.session.commit()
        except:
            elixir.session.rollback()
            raise

cherrypy.tools.ElixirTransaction = ElixirTransaction()

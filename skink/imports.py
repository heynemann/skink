#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../"))
sys.path.insert(0, root_path)

lib_path = join(root_path, "skink", "lib")
sys.path.insert(0, lib_path)

#cherrypy
import cherrypy
from cherrypy.process import plugins

#elixir and sql alchemy
import sqlalchemy
from sqlalchemy.types import *
from sqlalchemy.orm.scoping import ScopedSession
import elixir
from elixir import *

#pygments
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter

#routes
from routes import *

#genshi
from genshi.core import Stream
from genshi.output import encode, get_serializer
from genshi.template import Context, TemplateLoader
from genshi.filters import HTMLFormFiller

#pyoc
from pyoc.ioc import IoC
from pyoc.config import InPlaceConfig

#simplejson
import simplejson

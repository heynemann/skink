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

from os.path import split, abspath, join, dirname

from jinja2 import Environment, FileSystemLoader
import cherrypy
from cherrypy import thread_data

__CONTROLLERS__ = []
__CONTROLLERSDICT__ = {}

def route(route, name=None):
    def dec(func):
        actual_name = func.__name__
        if name:
            actual_name = name
        conf = (
            actual_name, {
                'route': route,
                'method': func.__name__
            }
        )

        return func, conf

    return dec

def authenticated(func):
    def actual(*arguments, **kw):
        instance = arguments[0]

        instance.server.publish('on_before_user_authentication', {'server':instance, 'context':instance.context})

        user = instance.user
        if user:
            instance.server.publish('on_user_authentication_successful', {'server':instance, 'context':instance.context})
            return func(*arguments, **kw)
        else:
            instance.server.publish('on_user_authentication_failed', {'server':instance, 'context':instance.context})

    actual.__name__ = func.__name__
    actual.__doc__ = func.__doc__
    return actual

class MetaController(type):
    def __init__(cls, name, bases, attrs):
        if name not in ('MetaController', 'Controller'):
            __CONTROLLERS__.append(cls)
            __CONTROLLERSDICT__[name] = cls
            cls.__routes__ = []

            for attr, value in attrs.items():
                if isinstance(value, tuple) and len(value) is 2:
                    method, conf = value
                    setattr(cls, attr, method)
                    cls.__routes__.append(conf)

        super(MetaController, cls).__init__(name, bases, attrs)

class Controller(object):
    __metaclass__ = MetaController
    __routes__ = None

    def __init__(self):
        self.context = None
        self.server = None

    def log(self, message):
        if self.context.settings.Ion.as_bool('verbose'):
            cherrypy.log(message, "[%s]" % self.__class__.__name__)

    @classmethod
    def all(self):
        return __CONTROLLERS__

    @property
    def store(self):
        return thread_data.store

    @property
    def name(self):
        return self.__class__.__name__.lower().replace("controller", "")

    @property
    def user(self):
        try:
            return cherrypy.session.get('authenticated_user', None)
        except AttributeError:
            return None

    def login(self, user):
        cherrypy.session['authenticated_user'] = user

    def logoff(self):
        cherrypy.session['authenticated_user'] = None

    def register_routes(self, dispatcher):
        for route in self.__routes__:
            route_name = "%s_%s" % (self.name, route[0])
            dispatcher.connect(route_name, route[1]["route"], controller=self, action=route[1]["method"])

    def render_template(self, template_file, **kw):
        template_path = self.context.settings.Ion.template_path.lstrip("/")
        template_path = template_path and abspath(join(self.server.root_dir, template_path)) or abspath(join(self.server.root_dir, 'templates'))

        env = Environment(loader=FileSystemLoader(template_path))

        template = env.get_template(template_file)
        return template.render(user=self.user, **kw)

    def redirect(self, url):
        raise cherrypy.HTTPRedirect(url)


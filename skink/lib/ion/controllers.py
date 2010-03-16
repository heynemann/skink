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

import os
from os.path import split, abspath, join, dirname

from jinja2 import Environment, FileSystemLoader
import cherrypy
from cherrypy import thread_data

from cache import Cache

from ion.sqlalchemy_tool import session

__CONTROLLERS__ = []
__CONTROLLERSDICT__ = {}

def route(route, name=None, priority=50):
    def dec(func):
        actual_name = func.__name__
        if name:
            actual_name = name
        conf = (
            actual_name, {
                'route': route,
                'method': func.__name__,
                'priority': priority
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

            routes = []

            for attr, value in attrs.items():
                if isinstance(value, tuple) and len(value) is 2:
                    method, conf = value
                    routes.append((attr, method, conf, conf[1]['priority']))

            routes = sorted(routes, lambda i1, i2: cmp(i2[3], i1[3]))

            for attr, method, conf, priority in routes:
                setattr(cls, attr, method)
                cls.__routes__.append(conf)

        super(MetaController, cls).__init__(name, bases, attrs)

class Controller(object):
    __metaclass__ = MetaController
    __routes__ = None

    def __init__(self):
        self.server = None

    def log(self, message):
        if self.settings.Ion.as_bool('verbose'):
            cherrypy.log(message, "[%s]" % self.__class__.__name__)

    @classmethod
    def all(self):
        return __CONTROLLERS__

    @property
    def cache(self):
        return self.server.cache

    @property
    def settings(self):
        if not self.server:
            return None
        return self.server.context.settings

    @property
    def context(self):
        if not self.server:
            return None
        return self.server.context

    @property
    def store(self):
        return session

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
        template_path = self.server.template_path

        env = Environment(loader=FileSystemLoader(template_path))

        for filter_name in self.server.template_filters.keys():
            env.filters[filter_name] = self.server.template_filters[filter_name]

        template = env.get_template(template_file)
        return template.render(user=self.user, settings=self.settings, **kw)

    def send_template_by_mail(self, from_email, to_emails, subject, template_file, html=True, **kw):
        body = self.render_template(template_file, **kw)
        exit_code = self.send_using_sendmail(from_email, to_emails, subject, body, html=html)
        return exit_code

    def send_using_sendmail(self, from_email, to_emails, subject, body, html=True):
        SENDMAIL = "/usr/sbin/sendmail" # sendmail location
        p = os.popen("%s -t" % SENDMAIL, "w")
        p.write("From: %s\n" % from_email)
        p.write("To: %s\n" % (", ".join(to_emails)))
        p.write("Subject: %s\n" % subject)
        p.write("\n") # blank line separating headers from body

        if html:
            p.write('Content-Type: text/html; charset="us-ascii"\n')
            p.write('MIME-Version: 1.0')
            p.write('Content-Transfer-Encoding: 7bit')

        p.write(body)

        sts = p.close()

        if sts != 0:
            self.log("Sendmail exit status: %d" % sts)

        return sts

    def send_using_smtp(self, from_email, to_emails, subject, body):
        pass

    def redirect(self, url):
        raise cherrypy.HTTPRedirect(url)

    def healthcheck(self):
        healthcheck_text = self.settings.Ion.healthcheck_text

        result = self.server.test_connection()
        if not result:
            raise RuntimeError("The connection to the database failed with error: %s" % str(self.server.test_connection_error))

        return healthcheck_text or "WORKING"


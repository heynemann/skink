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

import skink.lib
import cherrypy
from ion import Controller, route

class LoginController(Controller):

    @route("/authentication")
    def authentication_login(self, login, password):
        if (login == self.settings.Skink.admin_user and password == self.settings.Skink.admin_pass):
            self.login(login)
            self.redirect("/")
        else:
            self.redirect("/authentication/invalid")

    @route("/authentication/logoff", priority=1)
    def authentication_logoff(self):
        self.logoff()
        self.redirect("/")

    @route("/authentication/invalid", priority=2)
    def invalid_authentication(self):
        return self.render_template("invalid_auth.html")


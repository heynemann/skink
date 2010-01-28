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

import sys
import os
from os.path import abspath, dirname, join
import optparse
import urllib

import Queue

import skink.lib
from ion import Server, Settings
from simple_db_migrate.cli import CLI
from simple_db_migrate.core import InPlaceConfig
from simple_db_migrate.main import Main

import cherrypy

from skink.src.services.plugins.builder import *
from skink.src.services.plugins.monitor import *

def main():
    """ Main function - parses args and runs action """
    parser = optparse.OptionParser(usage="%prog run or type %prog -h (--help) for help", description=__doc__, version="%prog")

    (options, args) = parser.parse_args()
    
    if not args:
        print "Invalid action. for help type skink_console.py -h (--help) for help"
        sys.exit(0)
 
    action = args[0]
    
    if action.lower() == "run":
        run_skink_server()

    if action.lower() == "createdb":
        run_migrations(drop_db=True)

    if action.lower() == "upgradedb":
        run_migrations(drop_db=False)

    sys.exit(0)

def on_user_authentication_failed_handler(data):
    raise cherrypy.HTTPRedirect("/authentication/%s" % urllib.quote(cherrypy.url(cherrypy.request.path_info)).replace("/", "@@"))

def run_skink_server():
    root_dir = abspath(dirname(__file__))
    server = Server(root_dir=root_dir)
    server.build_dir = join(root_dir, "ci_tmp")

    server.subscribe('on_user_authentication_failed', on_user_authentication_failed_handler)

    server.context.current_project = None
    server.context.current_command = None
    server.context.build_queue = Queue.deque()
    server.context.projects_being_built = Queue.deque()

    builder = BuilderPlugin(cherrypy.engine, server)
    builder.subscribe()

    monitor = MonitorPlugin(cherrypy.engine, server)
    monitor.subscribe()

    try:
        server.start("config.ini")
    except KeyboardInterrupt:
        server.stop()

def run_migrations(drop_db=False):
    root_dir = abspath(dirname(__file__))
    
    settings = Settings(root_dir)
    settings.load("config.ini")

    protocol = settings.Db.protocol
    username = settings.Db.user
    password = settings.Db.password
    host = settings.Db.host
    port = int(settings.Db.port)
    database = settings.Db.database

    config = InPlaceConfig(db_host=host, db_user=username, db_password=password, db_name=database, migrations_dir=join(root_dir, "db"))

    config.put("schema_version", None)
    config.put("show_sql", False)
    config.put("show_sql_only", False)
    config.put("new_migration", None)

    config.put("drop_db_first", drop_db)

    Main(config).execute()

if __name__ == "__main__":
    main()

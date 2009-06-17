#!/usr/bin/env python
# -*- coding:utf-8 -*-

u"""Skink - Simple Fun Continuous Integration Server
authors: `Bernardo Heynemann <heynemann@gmail.com> and José Cláudio Figueiredo <jcfigueiredo@gmail.com>`
"""
__revision__ = "$Id$"
__docformat__ = 'restructuredtext en'
 
import os
import optparse
import sys
from os.path import dirname, abspath, join
root_path = abspath(join(dirname(__file__), "../"))
sys.path.insert(0, root_path)

from skink.controllers.infra import Server
from skink.context import SkinkContext

from skink.lib.simple_db_migrate.cli import CLI
from skink.lib.simple_db_migrate.core import InPlaceConfig
from skink.lib.simple_db_migrate.main import Main

def main():
    """ Main function - parses args and runs action """
    parser = optparse.OptionParser(usage="%prog run or type %prog -h (--help) for help", description=__doc__, version="%prog" + __revision__)
    #parser.add_option("-p", "--pattern", dest="pattern", default="*.acc", help="File pattern. Defines which files will get executed [default: %default].")

    (options, args) = parser.parse_args()
    
    if not args:
        print "Invalid action. for help type skink_console.py -h (--help) for help"
        sys.exit(0)
 
    action = args[0]
    
    if action.lower() == "run":
        try:
            Server.start()
        except KeyboardInterrupt:
            Server.stop()

    if action.lower() == "createdb":
        run_migrations(drop_db=True)

    if action.lower() == "upgradedb":
        run_migrations(drop_db=False)

    sys.exit(0)

def run_migrations(drop_db=False):
    ctx = SkinkContext.current()
    config = InPlaceConfig(db_host=ctx.db_host, db_user=ctx.db_user, db_password=ctx.db_pass, db_name=ctx.db_name, migrations_dir=join(root_path, "db"))

    config.put("schema_version", None)
    config.put("show_sql", False)
    config.put("show_sql_only", False)
    config.put("new_migration", None)

    config.put("drop_db_first", drop_db)

    Main(config).execute()

if __name__ == "__main__":
    main()

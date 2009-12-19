#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
from os.path import abspath, dirname
import optparse

from skink.lib.ion import Server

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

def run_skink_server():
    root_dir = abspath(dirname(__file__))
    server = Server(root_dir=root_dir)
    try:
        server.start("config.ini")
    except KeyboardInterrupt:
        server.stop()

def run_migrations(drop_db=False):
    pass
    #ctx = SkinkContext.current()
    #config = InPlaceConfig(db_host=ctx.db_host, db_user=ctx.db_user, db_password=ctx.db_pass, db_name=ctx.db_name, migrations_dir=join(root_path, "db"))

    #config.put("schema_version", None)
    #config.put("show_sql", False)
    #config.put("show_sql_only", False)
    #config.put("new_migration", None)

    #config.put("drop_db_first", drop_db)

    #Main(config).execute()

if __name__ == "__main__":
    main()

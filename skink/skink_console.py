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
        Server.start()
    
    sys.exit(0)

if __name__ == "__main__":
    main()

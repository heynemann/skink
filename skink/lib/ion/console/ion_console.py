#!/usr/bin/env python
# -*- coding:utf-8 -*-

u"""Ion - MVC Web Framework
authors: `Bernardo Heynemann <heynemann@gmail.com>
"""
__revision__ = "$Id$"
__docformat__ = 'restructuredtext en'
 
import sys
import os
from os.path import abspath
import optparse

from providers import *

def main():
    """ Main function - parses args and runs action """
    parser = optparse.OptionParser(usage="%prog run or type %prog -h (--help) for help", description=__doc__, version="%prog" + __revision__)
    #parser.add_option("-p", "--pattern", dest="pattern", default="*.acc", help="File pattern. Defines which files will get executed [default: %default].")

    (options, args) = parser.parse_args()

    if not args:
        print "Invalid action. for help type ion help"
        sys.exit(0)

    action = args[0]

    providers = Provider.all()

    found_provider = False

    for provider_type in providers:
        provider = provider_type()
        if provider.key != action:
            continue

        found_provider = True

        provider.execute(abspath(os.curdir), options, args[1:])

    if not found_provider:
        print "Invalid option. for help type ion help"

    sys.exit(0)

if __name__ == "__main__":
    main()

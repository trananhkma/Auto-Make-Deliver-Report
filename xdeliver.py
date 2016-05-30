#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR: hieulq

from datetime import date, timedelta

import gerritssh as gssh
import logging
import optparse
import sys

### LOGGING

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    stream=sys.stderr)

### DEFAULT SETTINGS

OWNER = 'hieulq'
GERRIT_HOST = 'review.openstack.org'
GERRIT_PORT = 29418
START_TIME = (date.today() - timedelta(days=7)).isoformat()


def _check_date(value):
    try:
        return date.strftime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError("invalid date: %r" % value)


def main():
    parser = optparse.OptionParser()
    parser.add_option("-o", "--owner", dest="owner", action='store',
                      help="gerrit pwner [default: %default]", metavar="OWNER",
                      default=OWNER)
    parser.add_option("-s", "--server", dest="server", action='store',
                      help="gerrit server [default: %default]",
                      metavar="SERVER", default=GERRIT_HOST)
    parser.add_option("-p", "--port", dest="port", action='store',
                      type="int", help="gerrit port [default: %default]",
                      metavar="PORT", default=GERRIT_PORT)
    parser.add_option("--start-time", dest="start_time", action='store',
                      type="string", help="start time for querrying in gerrit",
                      metavar="STARTTIME", default=START_TIME)
    parser.add_option("-k", "--keyfile", dest="keyfile", action='store',
                      help="gerrit ssh keyfile [default: use local keyfile]",
                      metavar="FILE", default=None)
    (options, args) = parser.parse_args()
    owner = options.owner
    start_time = options.start_time
    port = options.port
    server = options.server
    keyfile = options.keyfile

    rsite = gssh.Site(server, owner, port, keyfile).connect()
    pss = gssh.Query('--commit-message',
               'status:merged owner:' + owner +
               ' since:' + start_time).execute_on(rsite)
    print pss


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR: hieulq

from datetime import datetime, date, timedelta
from collections import namedtuple

import gerritssh as gssh
import logging
import optparse
import os
import requests
import shutil
import sys
import txt2pdf

# LOGGING

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    stream=sys.stderr)

# DEFAULT SETTINGS

PROTO = 'https://'
OWNER = 'hieulq'
GERRIT_HOST = 'review.openstack.org'
GERRIT_PORT = 29418
START_TIME = (date.today() - timedelta(days=7)).isoformat()
OUTPUT = 'Deliver'

BP_KEYWORDS = ['blueprint ', 'bp:']
BUG_KEYWORDS = ['Closes-Bug: #', 'Closes-bug: #',
                'Partial-Bug: #', 'Partial-bug: #']

LOC_FILE = "/".join([os.getcwd(), 'loc.txt'])
LF = None


def check_date(value):
    try:
        datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date: %r" % value)


def get_content(patch_url):
    r = requests.get(patch_url)
    if r.ok:
        return r.content


def create_file(project_name, bug_name, patch_url, pinfo=None, patch_num=1):
    if project_name:
        filename = '%s_%s_PS%s.txt' % (project_name, bug_name, patch_num)
    else:
        filename = '%s_PS%s.txt' % (bug_name, patch_num)
    LOG.info('|_______ Getting patch: %s', patch_num)
    while True:
        try:
            with open(filename, 'w+') as f:
                f.write(get_content(patch_url))
        except TypeError:
            LOG.error('Failed to get PS raw data! Retrying..')
            continue
        break
    outfile = txt2pdf.convert(filename)
    os.remove(filename)
    if len(pinfo) == 3:
        LF.write((outfile + '|' + str(pinfo[0]) + '|' + str(
            pinfo[1]) + '|' + pinfo[2] + '\n').encode('utf-8'))
    else:
        LF.write((outfile + '|' + str(pinfo[0]) + '|' + str(
            pinfo[1]) + '\n').encode('utf-8'))
    LOG.info('\_______ Finish creating: %s', outfile)


def create_folder(project_name, topic, msg=None):
    if project_name:
        directory = '%s_%s' % (project_name, topic)
    else:
        directory = '%s' % topic
    if not os.path.exists(directory):
        LOG.info('|_______ Create folder: %s', directory)
        os.makedirs(directory)
        if msg is not None:
            LF.write(directory + '|' + msg + '\n')
    else:
        LOG.info('|_______ Folder %s existed!', directory)
        if msg is not None:
            LF.write((directory + '|' + msg + '\n').encode('utf-8'))
    return directory


def get_topic_name(ps):
    topic = namedtuple('topic', ['bp', 'bug', 'change'])
    msg = ps.raw['commitMessage']
    topic.bp = ''
    topic.bug = ''
    topic.change = 'patch_%s' % ps.number

    bp_count = 0
    for bp in BP_KEYWORDS:
        count = msg.count(bp)
        for x in range(0, count):
            topic.bp += 'BP_%s' % \
                         msg.split(bp)[x + 1].splitlines()[0].rstrip()
            if count > 1:
                topic.bp += '_'
        if count > 1:
            topic.bp = topic.bp[:-1]
        if count:
            bp_count += 1
            topic.bp += '_'
    if bp_count:
        topic.bp = topic.bp[:-1]

    bug_count = 0
    for bug in BUG_KEYWORDS:
        count = msg.count(bug)
        for x in range(0, count):
            topic.bug += 'bug_%s' % \
                         msg.split(bug)[x + 1].splitlines()[0].rstrip()
            if count > 1:
                topic.bug += '_'
        if count > 1:
            topic.bug = topic.bug[:-1]
        if count:
            bug_count += 1
            topic.bug += '_'
    if bug_count:
        topic.bug = topic.bug[:-1]

    return topic


def main():
    global LF
    parser = optparse.OptionParser(usage="usage: %prog [options]",
                                   version="%prog 1.0")
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
                      type="string", help="start time for querrying in "
                                          "gerrit, in format: YYYY-MM-DD",
                      metavar="STARTTIME", default=START_TIME)
    parser.add_option("-k", "--keyfile", dest="keyfile", action='store',
                      help="gerrit ssh keyfile [default: use local keyfile]",
                      metavar="FILE", default=None)
    parser.add_option("-P", "--passphrase", dest="passphrase", action='store',
                      help="passphrase in case of enrypting keyfile",
                      metavar="PASS", default=None)
    parser.add_option("-u", "--user", dest="user", action='store',
                      help="gerrit user to querry [default: %default]",
                      metavar="USER", default=OWNER)
    parser.add_option("-d", "--del", dest="bdel", action='store',
                      type="int", help="whether to delete delivery folder "
                                       "and loc file [default: %default]",
                      metavar="OPTION", default=0)
    (options, args) = parser.parse_args()
    check_date(options.start_time)
    owner = options.owner
    start_time = options.start_time
    port = options.port
    server = options.server
    keyfile = options.keyfile
    passp = options.passphrase
    user = options.user
    bdel = options.bdel

    rsite = gssh.Site(server, owner, port, keyfile, passp).connect()
    plist = gssh.Query('--commit-message',
                       'owner:' + user +
                       ' AND (status:merged OR status:pending)' +
                       ' since:' + start_time).execute_on(rsite)
    LOG.info("| Total gerrit results: %d", len(plist))

    if bdel == 1:
        shutil.rmtree(OUTPUT, True)
        if os.path.exists(LOC_FILE):
            os.remove(LOC_FILE)

    LF = open(LOC_FILE, 'a')

    # Create delivery folder
    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)
    if OUTPUT.startswith('/'):
        root_dir = OUTPUT
    else:
        root_dir = "/".join([os.getcwd(), OUTPUT])

    for p in plist:
        LOG.info("|_ Generating doc from gerrit patch: %s ", p.number)
        os.chdir(root_dir)

        project_name = '[' + p.repo_name.split('/')[-1] + ']'
        topic = get_topic_name(p)
        pss = p.patchsets
        patch_urls = {}
        if topic.bug:
            name = topic.bug
        else:
            name = topic.change
        for num, ps in pss.iteritems():
            patch_urls[num] = PROTO + GERRIT_HOST + \
                '/gitweb?p=' + p.repo_name + \
                '.git;a=patch;h=' + \
                ps.raw['revision']

        LOG.info('|____ Project: %s', project_name)
        LOG.info('|____ Topic: %s', name)
        LOG.info('|____ PS count: %s', len(patch_urls))
        patch_name = project_name
        if topic.bp:
            directory = create_folder(patch_name, topic.bp)
            os.chdir("/".join([os.getcwd(), directory]))
            patch_name = None
        if len(patch_urls) == 1:
            create_file(patch_name, name,  patch_urls[1], (
                        p.patchsets[1].raw['sizeInsertions'],
                        p.patchsets[1].raw['sizeDeletions'],
                        p.raw['commitMessage'].
                        split('Change-Id')[0].replace('\n', ' ')))
        else:
            directory = create_folder(patch_name, name,
                                      p.raw['commitMessage'].
                                      split('Change-Id')[0].replace('\n', ' '))
            os.chdir("/".join([os.getcwd(), directory]))
            tmp_name = name
            if topic.bug and topic.change:
                tmp_name = topic.bug + '_' + topic.change 
            for patch_num, patch_url in patch_urls.iteritems():
                create_file(None, tmp_name, patch_url, (
                            p.patchsets[patch_num].raw['sizeInsertions'],
                            p.patchsets[patch_num].raw['sizeDeletions']),
                            patch_num=patch_num)
    LF.close()
    LOG.info("|_ FIN!")


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    main()

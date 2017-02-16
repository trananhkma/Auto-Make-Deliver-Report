#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR: hieulq

import datetime
import requests

# Change this list based on your member's info
USER_LIST = ['hieulq', 'duonghq', 'tovin07', 'daidv']

# No need to change in case of changing Stackalytics API or changing cycle
CONTRIB_URL = "http://stackalytics.com/api/1.0/contribution"
RELEASE = "ocata"

# Common query info
PROJECT_TYPE = "openstack"
COMPANY = "fujitsu"
PAYLOAD = {'release': RELEASE, 'project_type': PROJECT_TYPE,
           'company': COMPANY}

TODAY = datetime.date.today()


def main():
    total_ps, total_cm, total_rv, total_mbp, total_rbp = 0, 0, 0, 0, 0
    status = True

    for user in USER_LIST:
        PAYLOAD['user_id'] = user
        resp = requests.get(CONTRIB_URL, params=PAYLOAD)
        if resp.ok:
            parsed = resp.json()['contribution']
            user_ps_count = parsed['patch_set_count']
            user_cm_count = parsed['commit_count']
            user_bp_merge = parsed['completed_blueprint_count']
            user_bp_review = parsed['drafted_blueprint_count']
            user_rv_count = parsed['marks']['-1'] + parsed['marks']['1'] + \
                parsed['marks']['-2'] + parsed['marks']['2']
            
            print("* %s's review: %d" % (user, user_rv_count))
            
            total_ps += user_ps_count
            total_cm += user_cm_count
            total_rv += user_rv_count
            total_mbp += user_bp_merge
            total_rbp += user_bp_review
        else:
            print("There are something wrong with user %s !" % user)
            status = False

    if status:
        print("===%s: Team contribution report===" % TODAY)
        print("Total in-review BP: %d" % total_rbp)
        print("Total merged BP: %d" % total_mbp)
        print("Total commits count: %d" % total_cm)
        print("Total reviews count: %d" % total_rv)
        print("Total patches uploaded: %d" % total_ps)
        print("=======")


if __name__ == '__main__':
    if __name__ == '__main__':
        main()

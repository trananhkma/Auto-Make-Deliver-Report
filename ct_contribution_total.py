#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR: hieulq

import copy
import time
import requests

# Change this list based on your member's info
USER_LIST = ['hieulq', 'tovin07']

# No need to change in case of changing Stackalytics API or changing cycle
CONTRIB_URL = "http://stackalytics.com/api/1.0/contribution"
RELEASE = "queen"

# Common query info
PROJECT_TYPE = "openstack"
COMPANY = "fujitsu"
PAYLOAD = {'release': RELEASE, 'project_type': PROJECT_TYPE,
           'company': COMPANY}


def get_statistics(is_member=False):
    total_ps, total_cm, total_rv, total_mbp, total_rbp = 0, 0, 0, 0, 0
    params = copy.deepcopy(PAYLOAD)
    if is_member:
        params['start_date'] = int(time.time() - 604800)
        params['end_date'] = int(time.time())

    for user in USER_LIST:
        params['user_id'] = user
        resp = requests.get(CONTRIB_URL, params=params)
        if resp.ok:
            parsed = resp.json()['contribution']
            user_ps_count = parsed['patch_set_count']
            user_cm_count = parsed['commit_count']
            user_bp_merge = parsed['completed_blueprint_count']
            user_bp_review = parsed['drafted_blueprint_count']
            user_rv_count = parsed['marks']['-1'] + parsed['marks']['1'] + \
                parsed['marks']['-2'] + parsed['marks']['2']

            if is_member:
                print("* %s's review increase: %d" % (user, user_rv_count))
            else:
                print("* %s's review: %d" % (user, user_rv_count))

            total_ps += user_ps_count
            total_cm += user_cm_count
            total_rv += user_rv_count
            total_mbp += user_bp_merge
            total_rbp += user_bp_review
        else:
            print("There are something wrong with user %s !" % user)
            return None

    return total_ps, total_cm, total_rv, total_mbp, total_rbp


def main():
    print("===== Member's total review count =====")
    team_res = get_statistics(is_member=False)
    if team_res:
        print("===== %s: Team contribution report =====" % time.ctime())
        print("* Total in-review BP: %d" % team_res[4])
        print("* Total merged BP: %d" % team_res[3])
        print("* Total commits count: %d" % team_res[1])
        print("* Total reviews count: %d" % team_res[2])
        print("* Total in-review patches: %d" % (team_res[0] - team_res[1]))
        print("===== FIN ======")

    print("===== Member's contribution compare with last week =====")
    member_res = get_statistics(is_member=True)
    if member_res:
        print("* Total commits since last week: %d" % member_res[1])
        print("* Total patches since last week: %d" %
              (member_res[0] - member_res[1]))


if __name__ == '__main__':
    main()

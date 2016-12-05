# -*- coding: utf-8 -*-

from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import requests
import os

import txt2pdf


ROOT = 'https://review.openstack.org/'
INPUT = 'input.txt'
OUTPUT = 'Deliver'
FIREFOX_BIN = '/usr/bin/firefox'


def get_input(filename=INPUT):
    with open(filename, 'r') as f:
        return [line.strip() for line in f]


def get_html(gerrit_url):
    driver = webdriver.Firefox(firefox_binary=FirefoxBinary(FIREFOX_BIN))
    driver.get(gerrit_url)
    sleep(5)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    driver.close()
    return html


def get_patch_count(html):
    return int(html.split('Patch Sets (')[1].split('/')[0])


def get_commit_url(html):
    return html.split('(gitweb)')[0].split('<a href="')[-1].split('"')[0]


def get_patch_urls(gerrit_url, html):
    patch_count = get_patch_count(html)
    patch_urls = {}
    patch_urls[patch_count] = ROOT + get_commit_url(html).replace('commitdiff', 'patch')
    while patch_count > 1:
        patch_count -= 1
        _html = get_html(gerrit_url + str(patch_count))
        patch_urls[patch_count] = ROOT + get_commit_url(_html).replace('commitdiff', 'patch')
    return patch_urls


def get_project_name(html):
    return "[%s]" % html.split('<th>Project</th>')[1].split('</a>')[0].split('/')[-1]


def get_bug_name(html):
    change = html.split('Change <a')[1].split('</a>')[0].split('">')[-1]
    if 'Closes-Bug: #' in html:
        return 'bug_%s' % html.split('Closes-Bug: #')[1].split('</a>')[0]
    elif 'Closes-bug: #' in html:
        return 'bug_%s' % html.split('Closes-bug: #')[1].split('</a>')[0]
    elif 'Partial-Bug: #' in html:
        return (
            'bug_%s' % html.split('Partial-Bug: #')[1].split('</a>')[0],
            'patch_%s' % change
        )
    elif 'Partial-bug: #' in html:
        return (
            'bug_%s' % html.split('Partial-bug: #')[1].split('</a>')[0],
            'patch_%s' % change
        )
    elif 'blueprint ' in html:
        return (
            'bp_%s' % html.split('blueprint ')[-1].split('</a>')[0],
            'patch_%s' % change
        )
    elif 'bp:' in html:
        return (
            'bp_%s' % html.split('bp:')[-1].split('</a>')[0],
            'patch_%s' % change
        )
    else:
        return 'patch_%s' % change


def get_content(patch_url):
    r = requests.get(patch_url)
    if r.ok:
        return r.content


def create_file(project_name, bug_name, patch_url, patch_num=1):
    filename = '%s_%s_PS%s.txt' % (project_name, bug_name, patch_num)
    print 'Getting patch', patch_num
    while True:
        try:
            with open(filename, 'w+') as f:
                f.write(get_content(patch_url))
        except TypeError:
            print 'Failed! Retrying...'
            continue
        print 'Done.'
        break
    outfile = txt2pdf.convert(filename)
    os.remove(filename)
    print "Created", outfile


def create_folder(project_name, bug_name):
    foldername = '%s_%s' % (project_name, bug_name)
    directory = "%s/Patches" % foldername
    if not os.path.exists(directory):
        print 'Create folder', foldername
        os.makedirs(directory)
    return directory


def main():
    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)
    if OUTPUT.startswith('/'):
        root_dir = OUTPUT
    else:
        root_dir = "/".join([os.getcwd(), OUTPUT])
    inputs = get_input()
    for url in inputs:
        print 'Getting from', url
        os.chdir(root_dir)
        while True:
            try:
                html = get_html(url)
                project_name = get_project_name(html)
                bug_name = get_bug_name(html)
                patch_urls = get_patch_urls(url, html)
            except IndexError:
                print "Get html failed! Retrying..."
                continue
            print 'Done.'
            break
        print 'Project:', project_name
        print 'Bug name:', bug_name
        print 'PS count:', len(patch_urls)
        if isinstance(bug_name, tuple):
            directory = create_folder(project_name, bug_name[0])
            os.chdir("/".join([os.getcwd(), directory]))
            bug_name = bug_name[1]
        if len(patch_urls) == 1:
            create_file(project_name, bug_name, patch_urls[1])
        else:
            directory = create_folder(project_name, bug_name)
            os.chdir("/".join([os.getcwd(), directory]))
            for patch_num, patch_url in patch_urls.iteritems():
                create_file(project_name, bug_name, patch_url, patch_num)


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    main()

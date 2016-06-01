#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# tree.py
#
# Written by Doug Dahms
#
# Prints the tree structure for the path specified on the command line

from os import listdir, sep
from os.path import abspath, basename, isdir
from sys import argv

from pyPdf import PdfFileReader

import optparse

# Delimiter
PAGE_DECO = 91
LOC_DECO = 114

LOC_FILE = 'loc.txt'

TOTAL_PAGE_COUNT = 0
TOTAL_LOC_INSERTION = 0
TOTAL_LOC_DELETIONS = 0
PC_STR = 'Total Pages count:'
LOC_STR = 'Total Lines count:'


def recur_deli(time, type=0):
    if type == 0:
        return '-'*time
    elif type == 1:
        return ' '*time


def get_loc(filename=LOC_FILE):
    with open(filename, 'r') as f:
        return [line.strip() for line in f]


def get_page_num(file):
    global TOTAL_PAGE_COUNT
    if file.endswith('.pdf'):
        num = PdfFileReader(open(file, 'rb')).getNumPages()
        TOTAL_PAGE_COUNT += num
        return str(num)
    else:
        return '0'


def tree(dir, padding, print_files=False, isLast=False, isFirst=False,
         locs=None):
    if isFirst:
        print padding.decode('utf8')[:-1].encode('utf8') + dir
    else:
        if isLast:
            print padding.decode('utf8')[:-1].encode('utf8') + '\___' + \
                  basename(abspath(dir))
        else:
            print padding.decode('utf8')[:-1].encode('utf8') + '+---' + \
                  basename(abspath(dir))
    if print_files:
        files = listdir(dir)
    else:
        files = [x for x in listdir(dir) if isdir(dir + sep + x)]
    if not isFirst:
        padding += '   '
    files = sorted(files, key=lambda s: s.lower())
    count = 0
    last = len(files) - 1
    for i, file in enumerate(files):
        count += 1
        path = dir + sep + file
        isLast = i == last
        if isdir(path):
            if count == len(files):
                if isFirst:
                    tree(path, padding, print_files, isLast, False, locs)
                else:
                    tree(path, padding + ' ', print_files, isLast, False, locs)
            else:
                tree(path, padding + '|', print_files, isLast, False, locs)
        else:
            if isLast:
                l = len(padding) + len(file) + 5
                if file in locs:
                    print padding + '\___' + file + ' ' + \
                          recur_deli(LOC_DECO-l+1) + locs[file][0] + \
                          ' insertions(+), ' + locs[file][1].replace('-','') +\
                          ' deletions(-)'
                    print padding + recur_deli(10, 1) + '- ' + locs[file][2]
                else:
                    print padding + '\___' + file + ' ' + \
                          recur_deli(PAGE_DECO - l + 1) + get_page_num(path)
            else:
                l = len(padding) + len(file) + 5
                if file in locs:
                    print padding + '|---' + file + ' ' + \
                          recur_deli(LOC_DECO-l+1) + locs[file][0] + \
                          ' insertions(+), ' + locs[file][1].replace('-','') +\
                          ' deletions(-)'
                    print padding + '|' + recur_deli(9, 1) + \
                          '- ' + locs[file][2]
                else:
                    print padding + '|---' + file + ' ' + \
                          recur_deli(PAGE_DECO - l + 1) + get_page_num(path)


def main():
    global TOTAL_LOC_INSERTION
    global TOTAL_LOC_DELETIONS

    parser = optparse.OptionParser(usage="usage: %prog [options]",
                                   version="%prog 1.0")

    parser.add_option("-p", "--path", dest="path", action='store',
                      help="delivery folder path [default: %default]",
                      metavar="PATH", default='~/Deliver')

    (options, args) = parser.parse_args()
    path = options.path

    locr = get_loc()
    locs = {}
    if isdir(path):
        for line in locr:
            loc = line.split('|')
            locs[loc[0]] = (loc[1], loc[2], loc[3])
            TOTAL_LOC_INSERTION += int(loc[1])
            TOTAL_LOC_DELETIONS += int(loc[2])
        tree(path, '', True, False, True, locs)
        print '\n' + PC_STR + recur_deli(PAGE_DECO - len(PC_STR) + 1) + \
              str(TOTAL_PAGE_COUNT) + ' pages'
        print LOC_STR + recur_deli(LOC_DECO - len(LOC_STR) + 1) + \
              str(TOTAL_LOC_INSERTION) + ' insertion(+), ' + \
              str(abs(TOTAL_LOC_DELETIONS)) + ' deletions(-)'
    else:
        print 'ERROR: \'' + path + '\' is not a directory'


if __name__ == '__main__':
    main()

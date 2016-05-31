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

# Delimiter
PAGE_DECO = 93
LOC_DECO = 114

LOC_FILE = 'loc.txt'


def recur_deli(time):
    return '-'*time


def get_loc(filename=LOC_FILE):
    with open(filename, 'r') as f:
        return [line.strip() for line in f]


def tree(dir, padding, print_files=False, isLast=False, isFirst=False,
         locs=None):
    if isFirst:
        print padding.decode('utf8')[:-1].encode('utf8') + dir
    else:
        if isLast:
            print padding.decode('utf8')[:-1].encode('utf8') + '\___ ' + \
                  basename(abspath(dir))
        else:
            print padding.decode('utf8')[:-1].encode('utf8') + '+--- ' + \
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
                print padding + '\___ ' + file + ' ' + \
                      recur_deli(LOC_DECO-l) + locs[file][0] + \
                      ' insertions(+), ' + locs[file][1] + ' deletions(-)'
            else:
                l = len(padding) + len(file) + 5
                print padding + '|--- ' + file + ' ' + \
                      recur_deli(LOC_DECO-l) + locs[file][0] + \
                      ' insertions(+), ' + locs[file][1] + ' deletions(-)'


def usage():
    return '''Usage: %s [-f] 
Print tree structure of path specified.
Options:
PATH    Path to process''' % basename(argv[0])


def main():
    if len(argv) == 1:
        print usage()
    else:
        # print directories and files
        path = argv[2]
        locr = get_loc()
        locs = {}
        if isdir(path):
            for line in locr:
                loc = line.split(' ')
                locs[loc[0]] = (loc[1], loc[2])
            tree(path, '', True, False, True, locs)
        else:
            print 'ERROR: \'' + path + '\' is not a directory'

if __name__ == '__main__':
    main()
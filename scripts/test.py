#!/usr/bin/env python
# coding=utf-8

"""
Khresmoi MT tester. 

Usage:

    ./test.py -w|-m
    
    -w = test if worker is running and able to process requests.
    -m = test if Moses server is running. 
"""

from __future__ import unicode_literals
import sys
import getopt

__author__ = "Ondřej Dušek"
__date__ = "2013"


def test_moses():
    return True

def test_worker():
    return True

def display_usage():
    """\
    Display program usage information.
    """
    print >> sys.stderr, __doc__


if __name__ == '__main__':
    # parse options
    opts, filenames = getopt.getopt(sys.argv[1:], 'hwm')
    should_test_moses = False
    should_test_worker = False
    help = False
    for opt, arg in opts:
        if opt == '-w':
            test_worker = True
        elif opt == '-h':
            help = True
        elif opt == '-m':
            test_moses = True
    # display help
    if filenames or (not test_moses and not test_worker) or help:
        display_usage()
        sys.exit(1)
    test_ok = True
    if should_test_moses:
        test_ok &= test_moses()
    if should_test_worker:
        test_ok &= test_worker()
    sys.exit(0 if test_ok else 1)

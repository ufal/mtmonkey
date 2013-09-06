#!/usr/bin/env python
# coding=utf-8

"""
Helper functions for MT support scripts.
"""

import codecs
import sys


def open_handles(filenames, encoding):
    """\
    Open given files or STDIN/STDOUT in the given encoding.
    """
    if len(filenames) == 2:
        fh_out = codecs.open(filenames[1], 'w', encoding)
    else:
        fh_out = codecs.getwriter(encoding)(sys.stdout)
    if len(filenames) >= 1:
        fh_in = codecs.open(filenames[0], 'r', encoding)
    else:
        fh_in = codecs.getreader(encoding)(sys.stdin)
    return fh_in, fh_out


def process_lines(func, filenames, encoding):
    """\
    Stream process given files or STDIN/STDOUT with the given function
    and encoding.
    """
    fh_in, fh_out = open_handles(filenames, encoding)
    for line in fh_in:
        line = line.rstrip('\r\n')
        line = func(line)
        print >> fh_out, line

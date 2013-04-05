#!/usr/bin/env python
# coding=utf-8

"""
Helper functions for MT support scripts.
"""

import codecs
import sys


def process_lines(func, filenames, encoding):
    """\
    Stream process given files or STDIN/STDOUT with the given function
    and encoding.
    """
    # open input and output streams
    if len(filenames) == 2:
        fh_out = codecs.open(filenames[1], 'w', encoding)
    else:
        fh_out = codecs.getwriter(encoding)(sys.stdout)
    if len(filenames) >= 1:
        fh_in = codecs.open(filenames[0], 'r', encoding)
    else:
        fh_in = codecs.getreader(encoding)(sys.stdin)
    for line in fh_in:
        line = func(line)
        print >> fh_out, line

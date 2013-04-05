#!/usr/bin/env python
# coding=utf-8

"""
A simple de-tokenizer for MT post-processing.

Library usage:

Command-line usage:

    ./detokenize.py [-e ENCODING] [input-file output-file]
    
    -e = use the given encoding (default: UTF-8)
      
    If no input and output files are given, the de-tokenizer will read
    STDIN and write to STDOUT.
"""

from __future__ import unicode_literals
from regex import Regex, UNICODE
from fileprocess import process_lines
import sys
import logging
import getopt

__author__ = "Ondřej Dušek"
__date__ = "2013"

DEFAULT_ENCODING = 'UTF-8'


class Detokenizer(object):
    """\
    A simple de-tokenizer class.
    """

    def __init__(self, options={}):
        """\
        Constructor (pre-compile all needed regexes).
        """
        # process options
        self.lowercase = 'lowercase' in options
        # compile regexes

    def detokenize(self, text):
        """\
        Detokenize the given text using current settings.
        """
        # text = ' ' + text + ' '
        # TODO
        return text


def display_usage():
    """\
    Display program usage information.
    """
    print >> sys.stderr, __doc__


if __name__ == '__main__':
    # parse options
    opts, filenames = getopt.getopt(sys.argv[1:], 'e:')
    options = {}
    help = False
    encoding = DEFAULT_ENCODING
    for opt, arg in opts:
        if opt == '-e':
            encoding = arg
    # display help
    if len(filenames) > 2 or help:
        display_usage()
        sys.exit(1)
    # process the input
    detok = Detokenizer(options)
    process_lines(detok.detokenize, filenames, encoding)

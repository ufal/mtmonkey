#!/usr/bin/env python
# coding=utf-8

"""
A simple sentence splitter for MT pre-processing.

Library usage:

Command-line usage:

    ./split_sentences.py [-e ENCODING] [input-file output-file]
    
    -e = use the given encoding (default: UTF-8)
      
    If no input and output files are given, the sentence splitter will read
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


class SentenceSplitter(object):
    """\
    A simple sentence splitter class.
    """

    SENT_STARTER = '([\'\"\(\[\¿\¡\p{Pi}]* *[\p{Upper}])'
    SENT_STARTER_PUNCT = '([\'\"\(\[\¿\¡\p{Pi}]+ *[\p{Upper}])'
    FINAL_PUNCT = ' *[\'\"\)\]\p{IsPf}]+'

    def __init__(self, options={}):
        """\
        Constructor (pre-compile all needed regexes).
        """
        # process options
        self.return_lists = True if options.get('lists') else False
        # compile regexes
        self.__non_period = Regex('([?!]|\.{2,}) +' +
                                  self.SENT_STARTER, UNICODE)
        self.__in_punct = Regex('([?!\.]' + FINAL_PUNCT + ') +' +
                                self.SENT_STARTER, UNICODE)
        self.__punct_follows = Regex('([?!]|\.{2,}) +' +
                                  self.SENT_STARTER_PUNCT, UNICODE)
        # periods should be done better
        self.__period = Regex('\. +' + self.SENT_STARTER, UNICODE)

    def split_sentences(self, text):
        """\
        Detokenize the given text using current settings.
        """
        text = ' ' + text + ' '
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
    splitter = SentenceSplitter(options)
    process_lines(lambda text: "\n".join(splitter.split_sentences(text)),
                  filenames, encoding)

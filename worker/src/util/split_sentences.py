#!/usr/bin/env python
# coding=utf-8

"""
A simple sentence splitter for MT pre-processing.

Library usage:

    from util.split_sentences import SentenceSplitter
    s = SentenceSplitter()
    split = s.split_sentences(text)
    
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

    # TODO look at quote characters, CZ quotes possibly have wrong
    # Unicode classes!

    # sentence starters (possibly some starting punctuation) + upper-case char.
    SENT_STARTER = r'([\'\"\(\[\¿\¡\p{Pi}]* *[\p{Upper}])'
    # sentence starters with compulsory punctuation
    SENT_STARTER_PUNCT = r'([\'\"\(\[\¿\¡\p{Pi}]+ *[\p{Upper}])'
    # final punctuation
    FINAL_PUNCT = r' *[\'\"\)\]\p{Pf}]+'

    def __init__(self, options={}):
        """\
        Constructor (pre-compile all needed regexes).
        """
        # compile regexes
        self.__spaces = Regex(r'\s+')
        self.__space_at_end = Regex(r'(^|\n) ')
        self.__space_at_begin = Regex(r' ($|\n)')
        self.__non_period = Regex(r'([?!]|\.{2,}) +' +
                                  self.SENT_STARTER, UNICODE)
        self.__in_punct = Regex(r'([?!\.]' + self.FINAL_PUNCT + r') +' +
                                self.SENT_STARTER, UNICODE)
        self.__punct_follows = Regex(r'([?!]|\.{2,}) +' +
                                  self.SENT_STARTER_PUNCT, UNICODE)
        # TODO periods should be done better
        self.__period = Regex(r'(\.) +' + self.SENT_STARTER, UNICODE)

    def split_sentences(self, text):
        """\
        Split sentences in the given text using current settings.
        """
        # clean
        text = self.__spaces.sub(r' ', text)
        text = self.__space_at_begin.sub(r'\1', text)
        text = self.__space_at_end.sub(r'\1', text)
        # split
        text = self.__non_period.sub(r'\1\n\2', text)
        text = self.__in_punct.sub(r'\1\n\2', text)
        text = self.__punct_follows.sub(r'\1\n\2', text)
        text = self.__period.sub(r'\1\n\2', text)
        return text.split("\n")


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

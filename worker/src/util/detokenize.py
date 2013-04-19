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

    # Moses special characters de-escaping
    ESCAPES = [('&bar;', '|'),
               ('&lt;', '<'),
               ('&gt;', '>'),
               ('&bra;', '['),
               ('&ket;', ']'),
               ('&amp;', '&')]  # should go last to prevent double de-escaping

    def __init__(self, options={}):
        """\
        Constructor (pre-compile all needed regexes).
        """
        # process options
        self.moses_deescape = True if options.get('moses_deescape') else False
        self.language = options.get('language', 'en')
        # compile regexes
        self.__currency_or_init_punct = Regex(r'^[\p{Sc}\(\[\{\¿\¡]+$')
        self.__noprespace_punct = Regex(r'^[\,\.\?\!\:\;\\\%\}\]\)]+$')
        # language-specific regexes
        self.__fr_prespace_punct = Regex(r'^[\?\!\:\;\\\%]$')
        self.__en_contractions = Regex(r'^\p{Alpha}+(\'ll|n\'t)$')

    def detokenize(self, text):
        """\
        Detokenize the given text using current settings.
        """
        # split text
        words = text.split(' ')
        # paste text back, omitting spaces where needed 
        text = ''
        pre_spc = ' '
        for pos, word in enumerate(words):
            # TODO CJK chars
            # no space after currency and initial punctuation
            if self.__currency_or_init_punct.match(word):
                text += pre_spc + word
                pre_spc = ''
            # no space before commas etc. (exclude some punctuation for French)
            elif self.__noprespace_punct.match(word) and \
                    (self.language != 'fr' or not
                     self.__fr_prespace_punct.match(word)):
                text += word
                pre_spc = ' '
            # contractions for English
            elif self.language == 'en' and word == "'" \
                    and pos > 0 and pos < len(words) - 1 \
                    and self.__en_contractions.match(words[pos - 1] + word +
                                                     words[pos + 1]):
                text += word
                pre_spc = ''
            # TODO rest
            else:
                text += pre_spc + word
                pre_spc = ' '
        # escape chars that are special to Moses
        if self.moses_deescape:
            for char, repl in self.ESCAPES:
                text = text.replace(char, repl)
        # return the result (strip leading/trailing space)
        return text.strip()


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

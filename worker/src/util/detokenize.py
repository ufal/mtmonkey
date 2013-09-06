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
from regex import Regex, UNICODE, IGNORECASE
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

    # Contractions for different languages
    CONTRACTIONS = {'en': r'^\p{Alpha}+(\'(ll|ve|re|[dsm])|n\'t)$',
                    'fr': r'^([cjtmnsdl]|qu)\'\p{Alpha}+$',
                    'es': r'^[dl]\'\p{Alpha}+$',
                    'it': r'^\p{Alpha}*(l\'\p{Alpha}+|[cv]\'è)$',
                    'cs': r'^\p{Alpha}+[-–](mail|li)$', }

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
        self.__cjk_chars = Regex(r'[\u1100-\u11FF\u2E80-\uA4CF\uA840-\uA87F'
                                 + r'\uAC00-\uD7AF\uF900-\uFAFF\uFE30-\uFE4F'
                                 + r'\uFF65-\uFFDC]')
        # language-specific regexes
        self.__fr_prespace_punct = Regex(r'^[\?\!\:\;\\\%]$')
        self.__contract = Regex(self.CONTRACTIONS[self.language], IGNORECASE)

    def detokenize(self, text):
        """\
        Detokenize the given text using current settings.
        """
        # split text
        words = text.split(' ')
        # paste text back, omitting spaces where needed 
        text = ''
        pre_spc = ' '
        quote_count = {'\'': 0, '"': 0, '`': 0}
        for pos, word in enumerate(words):
            # remove spaces in between CJK chars
            if self.__cjk_chars.match(text[-1:]) and \
                    self.__cjk_chars.match(word[:1]):
                text += word
                pre_spc = ' '
            # no space after currency and initial punctuation
            elif self.__currency_or_init_punct.match(word):
                text += pre_spc + word
                pre_spc = ''
            # no space before commas etc. (exclude some punctuation for French)
            elif self.__noprespace_punct.match(word) and \
                    (self.language != 'fr' or not
                     self.__fr_prespace_punct.match(word)):
                text += word
                pre_spc = ' '
            # contractions with comma or hyphen 
            elif word in "'-–" and pos > 0 and pos < len(words) - 1 \
                    and self.__contract.match(''.join(words[pos - 1:pos + 2])):
                text += word
                pre_spc = ''
            # handle quoting
            elif word in '\'"„“”‚‘’`':
                # detect opening and closing quotes by counting 
                # the appropriate quote types
                quote_type = word
                if quote_type in '„“”':
                    quote_type = '"'
                elif quote_type in '‚‘’':
                    quote_type = '\''
                # exceptions for true Unicode quotes in Czech & German
                if self.language in ['cs', 'de'] and word in '„‚':
                    quote_count[quote_type] = 0
                elif self.language in ['cs', 'de'] and word in '“‘':
                    quote_count[quote_type] = 1
                # special case: possessives in English ("Jones'" etc.)                    
                if self.language == 'en' and text.endswith('s'):
                    text += word
                    pre_spc = ' '
                # really a quotation mark
                else:
                    # opening quote
                    if quote_count[quote_type] % 2 == 0:
                        text += pre_spc + word
                        pre_spc = ''
                    # closing quote
                    else:
                        text += word
                        pre_spc = ' '
                    quote_count[quote_type] += 1
            # keep spaces around normal words
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

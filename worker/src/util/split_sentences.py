#!/usr/bin/env python
# coding=utf-8

"""
A simple sentence splitter for MT pre-processing.

Library usage:

    from util.split_sentences import SentenceSplitter
    s = SentenceSplitter(options)
    split = s.split_sentences(text)
    
    Options is a dict that can contain the following keys:
    
    'language':      use the default non-breaking prefixes for the given 
                     language (the value should be the ISO-639-2 two-letter 
                     code of the language)
    'nobreak_file':  use the file path in value to read non-breaking prefixes 
    

Command-line usage:

    ./split_sentences.py [-h]
    ./split_sentences.py [-e ENCODING] [-l language|-b no-break-file] \\
                         [input-file output-file]
    
    -e = use the given encoding (default: UTF-8)
    -l = use the default non-breaking prefixes for the given language
         (the argument should be the ISO-639-2 two-letter code of the language)
    -b = use the given file path to read non-breaking prefixes
    -h = show this help
      
    If no language and no no-break prefixes are given, an empty set of prefixes
    will be used.
    
    If no input and output files are given, the sentence splitter will read
    STDIN and write to STDOUT.
"""

from __future__ import unicode_literals
from regex import Regex, UNICODE
import regex
from fileprocess import open_handles
import sys
import logging
import getopt
import os
import codecs

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
    SENT_STARTER = r'([\'\"\(\[\¿\¡\p{Pi}]* *[\p{Upper}\p{N}])'
    # sentence starters with compulsory punctuation
    SENT_STARTER_PUNCT = r'([\'\"\(\[\¿\¡\p{Pi}]+ *[\p{Upper}p{N}])'
    # final punctuation
    FINAL_PUNCT = r'[\'\"\)\]\p{Pf}\%]+'
    # non-breaking prefix directory
    NOBREAK_DIR = 'nonbreaking_prefixes'
    # non-breaking prefix file
    NOBREAK_FILE = 'nonbreaking_prefix.'

    def __init__(self, options={}):
        """\
        Constructor (pre-compile all needed regexes).
        """
        # load no-break prefixes for the given language
        self.__load_nobreaks(options.get('language'),
                             options.get('nobreak_file'))
        # compile regexes
        self.__spaces = Regex(r'\s+')
        self.__space_at_end = Regex(r'(^|\n) ')
        self.__space_at_begin = Regex(r' ($|\n)')
        self.__non_period = Regex(r'([?!]|\.{2,}) +' + self.SENT_STARTER)
        self.__in_punct = Regex(r'([?!\.] *' + self.FINAL_PUNCT + r') +' +
                                self.SENT_STARTER)
        self.__punct_follows = Regex(r'([?!\.]) +' + self.SENT_STARTER_PUNCT)
        self.__period = Regex(r'([\p{Alnum}\.\-]+)(' + self.FINAL_PUNCT +
                              r')? *$')
        self.__ucase_acronym = Regex(r'\.[\p{Upper}\-]+$')
        self.__numbers = Regex(r'^\p{N}')
        self.__sent_starter = Regex(self.SENT_STARTER)

    def split_sentences(self, text):
        """\
        Split sentences in the given text using current settings.
        """
        # clean
        text = self.__spaces.sub(r' ', text)
        text = self.__space_at_begin.sub(r'\1', text)
        text = self.__space_at_end.sub(r'\1', text)
        # break on special cases
        text = self.__non_period.sub(r'\1\n\2', text)
        text = self.__in_punct.sub(r'\1\n\2', text)
        text = self.__punct_follows.sub(r'\1\n\2', text)
        text = self.__period.sub(r'\1\n\2', text)
        # break on periods
        words = text.split('. ')
        text = ''
        for word, next_word in zip(words[:-1], words[1:]):
            text += word + '.'
            match = self.__period.search(word)
            # check periods
            if match:
                prefix, end_punct = match.groups()
                # never break on no-break prefixes, upper case acronyms
                # and numeric no-breaks before numbers
                if (prefix in self.__nobreaks and not end_punct) or \
                        self.__ucase_acronym.search(prefix) or \
                        (prefix in self.__numeric_nobreaks and
                         not end_punct and self.__numbers.match(next_word)):
                    text += ' '
                # break before sentence starters
                elif self.__sent_starter.match(next_word):
                    text += "\n"
                # don't break otherwise
                else:
                    text += ' '
            # don't break when there's no period
            else:
                text += ' '
        # append last token (we stopped iterating just before it)
        text += words[-1]
        # return the result
        return text.split("\n")


    def __load_nobreaks(self, language=None, filename=None):
        """\
        Load non-breaking prefixes for the given language from a default
        location or from the given file.
        """
        # initialize sets of non-breaking prefixes
        self.__nobreaks = set()
        self.__numeric_nobreaks = set()
        # obtain file name from language specification
        if filename is None and language is not None:
            filename = os.path.dirname(__file__) + os.sep + \
                    self.NOBREAK_DIR + os.sep + self.NOBREAK_FILE + language
        # try to load prefixes from file
        if filename and os.path.isfile(filename):
            fh = codecs.open(filename, 'r', 'UTF-8')
            for item in fh:
                item = item.strip()
                if item and not item.startswith('#'):
                    match = regex.match(r'^(.*)\s+#NUMERIC_ONLY#', item)
                    if match:
                        self.__numeric_nobreaks.add(match.group(1))
                    else:
                        self.__nobreaks.add(item)


def display_usage():
    """\
    Display program usage information.
    """
    print >> sys.stderr, __doc__


if __name__ == '__main__':
    # parse options
    opts, filenames = getopt.getopt(sys.argv[1:], 'e:l:b:h')
    options = {}
    help = False
    encoding = DEFAULT_ENCODING
    for opt, arg in opts:
        if opt == '-e':
            encoding = arg
        elif opt == '-l':
            options['language'] = arg
        elif opt == '-b':
            options['nobreak_file'] = arg
        elif opt == '-h':
            help = True
    # display help
    if len(filenames) > 2 or help:
        display_usage()
        sys.exit(1)
    # process the input
    splitter = SentenceSplitter(options)
    fh_in, fh_out = open_handles(filenames, encoding)
    buf = []
    for line in fh_in:
        line = line.rstrip("\r\n")
        if line != '':
            buf.append(line)
        else:
            print >> fh_out, "\n".join(splitter.split_sentences(' '.join(buf)))
            buf = []
    print >> fh_out, "\n".join(splitter.split_sentences(' '.join(buf)))


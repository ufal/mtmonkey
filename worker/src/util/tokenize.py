#!/usr/bin/env python
# coding=utf-8

"""
A simple tokenizer for MT preprocessing.
"""

from __future__ import unicode_literals
from regex import Regex
import codecs
import sys


class Tokenizer(object):
    """\
    A simple tokenizer class, capable of tokenizing given strings.
    """

    def __init__(self):
        """\
        Constructor (pre-compile all needed regexes).
        """
        self.__spaces = Regex(r'\s+')
        self.__ascii_junk = Regex(r'[\000-\037]')
        self.__special_chars = \
                Regex(r'(([^\p{IsAlnum}\s\.\,])\2*)')
        self.__to_single_quotes = Regex(r'[`‚‘’]')
        self.__to_double_quotes = Regex(r'(\'\'|[“”„])')
        self.__no_numbers = Regex(r'([^\p{N}])([,.])([^\p{N}])')
        self.__pre_numbers = Regex(r'([^\p{N}])([,.])([\p{N}])')
        self.__post_numbers = Regex(r'([\p{N}])([,.])([^\p{N}])')

    def tokenize(self, text):
        """\
        Tokenize the given text using current settings.
        """
        # spaces to single space
        text = self.__spaces.sub(' ', text)
        # remove ASCII junk
        text = self.__ascii_junk.sub('', text)
        # separate punctuation (consecutive items of same type stay together)
        text = self.__special_chars.sub(r' \1 ', text)
        # separate dots and commas everywhere except in numbers
        text = self.__no_numbers.sub(r'\1 \2 \3', text)
        text = self.__pre_numbers.sub(r'\1 \2 \3', text)
        text = self.__post_numbers.sub(r'\1 \2 \3', text)
        # normalize quotes
        text = self.__to_single_quotes.sub('\'', text)
        text = self.__to_double_quotes.sub('"', text)
        # spaces to single space
        text = self.__spaces.sub(' ', text)
        text = text.strip() + "\n"
        return text


if __name__ == '__main__':
    fh_in = codecs.getreader('UTF-8')(sys.stdin)
    fh_out = codecs.getwriter('UTF-8')(sys.stdout)
    tok = Tokenizer()
    for line in fh_in:
        line = tok.tokenize(line)
        print >> fh_out, line,

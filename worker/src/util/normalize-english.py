#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from regex import Regex, UNICODE
import sys
import codecs
import locale
import string

def ucfirst(s):
    if len(s) == 0:
        return s
    else:
        return s[0].upper() + s[1:]

class EnglishNormalizer:
    def __init__(self):
        self.quo = r'„“”"'
        self.apo = r"‚‘’‛`'"
        self.noquo = r"[^" + self.quo + r"]"
        self.noapo = r"[^" + self.apo + r"]"
        self.noquoapo = r"[^" + self.quo + self.apo + r"]"
        self.doubleopenmark = "DoUbLeOpEnMaRk"
        self.doubleclosemark = "DoUbLeClOsEMaRk"
        self.singleopenmark = "SiNgLeOpEnMaRk"
        self.singleclosemark = "SiNgLeClOsEMaRk"
        self.nowhite = r'[^' + string.whitespace + r']'

        self.repl = {
            "can't": "can not",
            "cannot": "can not",
            "ain't": "is not",
            "won't": "will not",
            "I'm": "I am",
            "I've": "I have",
            "you've": "you have",
            "we've": "we have",
            "they've": "they have",
            "I'll": "I will",
            "you'll": "you will",
            "he'll": "he will",
            "she'll": "she will",
            "we'll": "we will",
            "they'll": "they will",
            "you're": "you are",
            "we're": "we are",
            "they're": "they are",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
            "don't": "do not",
            "doesn't": "does not",
            "didn't": "did not",
            "shouldn't": "should not",
            "wouldn't": "would not",
            "couldn't": "could not",
            "mustn't": "must not",
            "needn't": "need not",
            "hasn't": "has not",
            "haven't": "have not",
            "hadn't": "had not",
            }

    def __fix_english_quotation_pairs(self, s):
        s = Regex(r"“(" + self.noquo + r")*”").sub(self.doubleopenmark + r"\1" + self.doubleclosemark, s)
        s = Regex(r'"(' + self.noquo + r')*"').sub(self.doubleopenmark + r"\1" + self.doubleclosemark, s)
        s = Regex(r"``(" + self.noquoapo + r")*''").sub(self.doubleopenmark + r"\1" + self.doubleclosemark, s)
        s = Regex(r"``(" + self.noquo + r")*''").sub(self.doubleopenmark + r"\1" + self.doubleclosemark, s)

        s = Regex(r"`(" + self.noapo + r")*'").sub(self.singleopenmark + r"\1" + self.singleclosemark, s)
        s = Regex(r"‚(" + self.noapo + r")*‘").sub(self.singleopenmark + r"\1" + self.singleclosemark, s)
        s = Regex(r"‘(" + self.noapo + r")*’").sub(self.singleopenmark + r"\1" + self.singleclosemark, s)

        s = Regex(r'"( )').sub(self.doubleclosemark + r"\1", s)
        s = Regex(r'"$').sub(self.doubleclosemark, s)
        s = Regex(r'"[' + string.punctuation + r']$').sub(self.doubleclosemark + r"\1", s)
        s = Regex(r'( )"').sub(r"\1" + self.doubleopenmark, s)
        s = Regex(r'^"').sub(self.doubleopenmark, s)
        s = Regex(r"(" + self.nowhite + r")''").sub(r"\1" + self.doubleclosemark, s)
        s = Regex(r"(" + self.nowhite + r")``").sub(r"\1" + self.doubleclosemark, s)
        s = Regex(r"''(" + self.nowhite + r")").sub(self.doubleopenmark + r"\1", s)
        s = Regex(r"``(" + self.nowhite + r")").sub(self.doubleopenmark + r"\1", s)

        s = Regex(self.doubleopenmark).sub(r"“", s)
        s = Regex(self.doubleclosemark).sub(r"”", s)

        s = Regex(self.singleopenmark).sub(r"‘", s)
        s = Regex(self.singleclosemark).sub(r"’", s)

        return s


    def normalize(self, s):
        s = Regex(r'^([' + string.whitespace + r'])*').sub("", s)
        s = Regex(r'([' + string.whitespace + r'])+').sub(" ", s)
        s = self.__fix_english_quotation_pairs(s)
        s = Regex(r"[´'’‛]").sub(r"'", s);
        s = Regex(r"[-–­֊᠆‐‑‒–—―⁃⸗﹣－⊞⑈︱︲﹘]+").sub(r"-", s);

        for k, v in self.repl.iteritems():
            s = Regex(k).sub(v, s)
            s = Regex(k.upper()).sub(v.upper(), s)
            s = Regex(ucfirst(k)).sub(ucfirst(v), s)
            # TODO _highlighted_ versions... probably not that important?

        s = Regex(r" n't ").sub(r" not ", s);
        return s

if __name__ == '__main__':
    normalizer = EnglishNormalizer()
    encoding = locale.getpreferredencoding()
    sys.stdin = codecs.getreader(encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(encoding)(sys.stdout)
    for line in sys.stdin:
        line = line.rstrip('\r\n')
        print normalizer.normalize(line)

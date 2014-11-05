#!/usr/bin/env python

from ufal.morphodita import *
from regex import Regex, UNICODE
import sys
import codecs
import locale

class Morphodita:
    def __init__(self, model_path):
        self.tagger = Tagger.load(model_path)
        self.forms = Forms()
        self.lemmas = TaggedLemmas()
        self.tokens = TokenRanges()
        self.tokenizer = self.tagger.newTokenizer()

    def __encode_entities(self, text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

    def __perform_case(self, lemma, token):
        lemma = Regex('[\^_-].*').sub("", lemma)
        if lemma == lemma.lower(): # lowercase
            return token.lower()
        if lemma == lemma[0].upper() + lemma[1 : ].lower(): # ucfirst
            return token[0].upper() + token[1 : ].lower()
        if lemma == lemma.upper(): # uppercase
            return token.upper()
        return token # mixed case, leave as is

    def tokenize(self, text, stc=False):
        text = self.__encode_entities(text)
        self.tokenizer.setText(text)
        out = ""
        t = 0
        while self.tokenizer.nextSentence(self.forms, self.tokens):
            if stc:
                self.tagger.tag(self.forms, self.lemmas)

            for i in range(len(self.tokens)):
                token = self.tokens[i]
                if t != token.start:
                    out += text[t : token.start]
                if len(out) != 0:
                    out += " "

                tokenstr = text[token.start : token.start + token.length]
                if stc:
                    tokenstr = self.__perform_case(self.lemmas[i].lemma, tokenstr)
                    
                out += tokenstr
                t = token.start + token.length
        if len(out) != 0 and t != len(text):
            out += " " + text[t : ]
        return Regex("  *").sub(" ", out)


if __name__ == '__main__':
    encoding = locale.getpreferredencoding()
    sys.stdin = codecs.getreader(encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(encoding)(sys.stdout)
    tokenizer = Morphodita(sys.argv[1])
    for line in sys.stdin:
        line = line.rstrip('\r\n')
        print tokenizer.tokenize(line, True)

#!/usr/bin/env python

from ufal.morphodita import *
from regex import Regex, UNICODE
import sys
import codecs
import locale

class Morphodita:
    def __init__(self, model_path):
        self.tagger = Tagger.load(model_path)
        self.tokenizer = self.tagger.newTokenizer()

    def __encode_entities(self, text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&pipe;').replace('"', '&quot;')

    def __perform_case(self, lemma, token):
        lemma = Regex('[\^_-].*').sub("", lemma)
        if lemma == lemma.lower(): # lowercase
            return token.lower()
        if lemma == lemma[0].upper() + lemma[1 : ].lower(): # ucfirst
            return token[0].upper() + token[1 : ].lower()
        if lemma == lemma.upper(): # uppercase
            return token.upper()
        return token # mixed case, leave as is

    def tokenize(self, text, stc=False, further=False, include_lemma=False):
        forms = Forms()
        lemmas = TaggedLemmas()
        tokens = TokenRanges()

        text = self.__encode_entities(text)
        self.tokenizer.setText(text)
        out = ""
        t = 0
        while self.tokenizer.nextSentence(forms, tokens):
            if stc:
                self.tagger.tag(forms, lemmas)

            for i in range(len(tokens)):
                token = tokens[i]
                if t != token.start:
                    out += text[t : token.start]
                if len(out) != 0:
                    out += " "

                tokenstr = text[token.start : token.start + token.length]
                if stc:
                    tokenstr = self.__perform_case(lemmas[i].lemma, tokenstr)
                   
                if include_lemma:
                    tokenstr += "|" + lemmas[i].lemma

                out += tokenstr
                t = token.start + token.length

        if len(out) != 0 and t != len(text):
            out += " " + text[t : ]

        out = Regex("  *").sub(" ", out)
        if further:
            if include_lemma:
                out = self.__further_tokenize_factored(out)
            else:
                out = self.__further_tokenize(out)

        print out
        return out

    # XXX hacky fix for factored input -- first factor is always the one to tokenize, others are copied
    def __further_tokenize_factored(self, text):
        out = []
        tokens = text.split(" ")
        for token in tokens:
            factors = token.split("|", 1)
            minitokens = self.__further_tokenize(factors[0]).split(" ")
            for minitoken in minitokens:
                out.append(minitoken + "|" + factors[1])
        return " ".join(out)

    def __further_tokenize(self, text):
        # unescape
        text = Regex(r"&pipe;").sub(r"|", text)
        text = Regex(r"&lt;").sub(r"<", text)
        text = Regex(r"&gt;").sub(r">", text)
        text = Regex(r"&amp;").sub(r"&", text)

        text = Regex(r"([\p{N}\p{P}\p{S}])([\p{L}])").sub(r"\1 \2", text)
        text = Regex(r"([\p{L}\p{P}\p{S}])([\p{N}])").sub(r"\1 \2", text)
        text = Regex(r"([\p{L}\p{N}\p{S}])([\p{P}])").sub(r"\1 \2", text)
        text = Regex(r"([\p{L}\p{N}\p{P}])([\p{S}])").sub(r"\1 \2", text)

        text = Regex(r"([\p{L}])([\p{N}\p{P}\p{S}])").sub(r"\1 \2", text)
        text = Regex(r"([\p{N}])([\p{L}\p{P}\p{S}])").sub(r"\1 \2", text)
        text = Regex(r"([\p{P}])([\p{L}\p{N}\p{S}])").sub(r"\1 \2", text)
        text = Regex(r"([\p{S}])([\p{L}\p{N}\p{P}])").sub(r"\1 \2", text)

        # re-escape
        text = Regex(r"&").sub(r"&amp;", text)
        text = Regex(r"\|").sub(r"&pipe;", text)
        text = Regex(r"<").sub(r"&lt;", text)
        text = Regex(r">").sub(r"&gt;", text)

        return text


if __name__ == '__main__':
    encoding = locale.getpreferredencoding()
    sys.stdin = codecs.getreader(encoding)(sys.stdin)
    sys.stdout = codecs.getwriter(encoding)(sys.stdout)
    tokenizer = Morphodita(sys.argv[1])
    for line in sys.stdin:
        line = line.rstrip('\r\n')
        print tokenizer.tokenize(line, True, True)

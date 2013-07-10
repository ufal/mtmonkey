#!/usr/bin/env python

import time
import uuid
import xmlrpclib
import operator
import os
from util.tokenize import Tokenizer
from util.detokenize import Detokenizer
from util.split_sentences import SentenceSplitter

class Translator:
    """Handles the 'translate' task for KhresmoiWorker"""

    def __init__(self, translate_port, recase_port):
        self.translate_proxy = xmlrpclib.ServerProxy("http://localhost:" + translate_port +  "/RPC2")
        self.recase_proxy = xmlrpclib.ServerProxy("http://localhost:" + recase_port +  "/RPC2")
        self.tokenizer = Tokenizer({'lowercase': True, 'moses_escape': True})
        self.detokenizer = Detokenizer()
        self.splitter = SentenceSplitter()

    def process_task(task):
        """Process translation task. Splits request into sentences, then translates and
        recases each sentence."""
        doalign = ('alignmentInfo' in task) and (task['alignmentInfo'] == 'true')
        src_lines = self.splitter.split_sentences(task['text'])
        translated = [self._translate(line, doalign) for line in src_lines]
        return {
            'translation': [
            {
                "translationId": uuid.uuid4().hex,
                "translated": translated
            }
            ]
        }
    
    def _translate(src, doalign):
        """Translate and recase one sentence. Optionally, word alignment
        between source and target is included in output."""

        # tokenize
        src_tokenized = self.tokenizer.tokenize(text)

        # translate
        translation = self.translate_proxy.translate({
            "text": src_tokenized,
            "align": doalign
        })
        
        # recase
        tgt_tokenized = self.recase_proxy.translate({
            "text": translation['text'] })['text'].strip()

        # detokenize
        tgt = detokenizer.detokenize(tgt_tokenized)
    
        result = {
            'text': tgt,
            'score': 100, # TODO actual score
            'rank': 0 # TODO
        }

        # optionally add word-alignment information
        if doalign:
            result.update({
                'src-tokenized': src_tokenized,
                'tgt-tokenized': tgt_tokenized,
                'alignment-raw': _add_tgt_end(translation['align'], tgt_tokenized)
            })

        return result
    
def _parse_align(orig, transl, align):
    """not used for now"""
    p = orig.split()
    b = [' '.join(p[a['src-start']:a['src-end'] + 1]) for a in align]

    o = transl.split()
    oi = sorted([int(w['tgt-start']) for w in align])
    oi.append(len(o) + 1)
    a = [' '.join(o[oi[x]:oi[x + 1]]) for x in xrange(len(oi) - 1)]

    return zip(a, b)

def _add_tgt_end(align, tgttok):
    ks = map(lambda x: x['tgt-start'], align)
    n = len(tgttok.split())
    ks.append(n)
    for i in xrange(len(align)):
        align[i]['tgt-end'] = ks[i + 1] - 1
    return align

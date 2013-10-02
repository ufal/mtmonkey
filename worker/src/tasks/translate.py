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

    def process_task(self, task):
        """Process translation task. Splits request into sentences, then translates and
        recases each sentence."""
        doalign = task.get('alignmentInfo', '').lower() in ['true', 't', 'yes', 'y', '1']
        dodetok = not task.get('detokenize', '').lower() in ['false', 'f', 'no', 'n', '0']
        nbestsize = min(task.get('nBestSize', 1), 10)
        src_lines = self.splitter.split_sentences(task['text'])
        translated = [self._translate(line, doalign, dodetok, nbestsize) for line in src_lines]
        return _backward_transform({
            'translationId': uuid.uuid4().hex,
            'sentences': translated
        }, doalign, dodetok)
    
    def _translate(self, src, doalign, dodetok, nbestsize):
        """Translate and recase one sentence. Optionally, word alignment
        between source and target is included in output."""

        # tokenize
        src_tokenized = self.tokenizer.tokenize(src)

        # translate
        translation = self.translate_proxy.translate({
            "text": src_tokenized,
            "align": doalign,
            "nbest": nbestsize,
            "nbest-distinct": True,
        })

# XXX remove me
#        f = open("mosesout.txt", "w")
#        print >>f, translation
#        f.close()
        
        rank = 0
        hypos = []
        for hypo in translation['nbest']:
            recased = self.recase_proxy.translate({"text": hypo['hyp']})['text'].strip()
            parsed_hypo = {
                'text': recased,
                'score': hypo['totalScore'],
                'rank': rank,
            }

            if dodetok:
                parsed_hypo['text'] = self.detokenizer.detokenize(recased)

            if doalign:
                parsed_hypo['tokenized'] = recased
                parsed_hypo['raw-alignment'] = _add_tgt_end(hypo['align'], recased)

            rank += 1
            hypos.append(parsed_hypo)

        result = {
            'src': src,
            'translated': hypos,
        }

        if dodetok:
            result['src-tokenized'] = src_tokenized

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

def _backward_transform(result, doalign, dodetok):
    """Transform the produced output structure to old format.
    Soon to be deprecated."""
    translation = []
    min_nbest_length = min([len(s['translated']) for s in result['sentences']])
    for rank in range(0, min_nbest_length):
        translated = []
        for sent in result['sentences']:
            oldformat = { 'src': sent['src'] }
            if dodetok:
                oldformat['src-tokenized'] = sent['src-tokenized']

            oldformat['text'] = sent['translated'][rank]['text']
            oldformat['rank'] = rank
            oldformat['score'] = sent['translated'][rank]['score']
            if doalign:
                oldformat['tgt-tokenized'] = sent['translated'][rank]['tokenized']
                oldformat['raw-alignment'] = sent['translated'][rank]['raw-alignment']

            translated.append(oldformat)

        translation.append({'translated': translated, 'translationId': result['translationId']})

    return { 'translation': translation }

#!/usr/bin/env python

import time
import uuid
import xmlrpclib
import operator
import os
from util.tokenize import Tokenizer
from util.detokenize import Detokenizer
from util.split_sentences import SentenceSplitter

def paragraph(text, doalign):
    splitter = SentenceSplitter()
    lines = splitter.split_sentences(text)
    return [translate(l, doalign) for l in lines]

def parse_align(orig, transl, align):
    p = orig.split()
    b = [' '.join(p[a['src-start']:a['src-end'] + 1]) for a in align]

    o = transl.split()
    oi = sorted([int(w['tgt-start']) for w in align])
    oi.append(len(o) + 1)
    a = [' '.join(o[oi[x]:oi[x + 1]]) for x in xrange(len(oi) - 1)]

    return zip(a, b)

def add_tgt_end(align, tgttok):
    ks = map(lambda x: x['tgt-start'], align)
    n = len(tgttok.split())
    ks.append(n)
    for i in xrange(len(align)):
        align[i]['tgt-end'] = ks[i + 1] - 1
    return align

def translate(text, doalign):
    # tokenize
    tokenizer = Tokenizer({'lowercase': True, 'moses_escape': True})
    src_tokenized = tokenizer.tokenize(text)

    # translate
    p = xmlrpclib.ServerProxy("http://localhost:8080/RPC2")
    translation = p.translate({ "text": text, "align": True })
    align = parse_align(text, translation['text'], translation['align'])
    text = translation['text']

    # recase
    r = xmlrpclib.ServerProxy("http://localhost:9000/RPC2")
    text = r.translate({ "text": text })['text']
    tgt_tokenized = ' '.join(text.split())

    # detokenize
    detokenizer = Detokenizer()
    text = detokenizer.detokenize(text)

    r1 = { 'text': text.strip(), 'score': 100, 'rank': 0 }
    if doalign:
##  'alignment': align,
        r1 = dict(r1.items() + {
            'src-tokenized': src_tokenized,
            'tgt-tokenized': tgt_tokenized,
            'alignment-raw': add_tgt_end(translation['align'], tgt_tokenized), }.items())
    return r1

def process_task(task):
    f = task['sourceLang']
    e = task['targetLang']
    t = task['text']
    a = ('alignmentInfo' in task) and (task['alignmentInfo'] == 'true')
    return {
        'translation': [
        {
            "translationId": uuid.uuid4().hex,
            "translated": paragraph(t, a),
        }
        ]
    }


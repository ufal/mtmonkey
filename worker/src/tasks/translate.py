#!/usr/bin/env python

import time
import uuid
import xmlrpclib
import operator
import os
from util.tokenize import Tokenizer
from util.detokenize import Detokenizer
from util.split_sentences import SentenceSplitter

def translate_paragraph(text, do_align, do_detok):
    splitter = SentenceSplitter()
    sents = splitter.split_sentences(text)
    return [translate_sentence(s, do_align, do_detok) for s in sents]

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

def translate_sentence(sent, do_align=False, do_detok=True):
    # tokenize
    tokenizer = Tokenizer({'lowercase': True, 'moses_escape': True})
    sent = tokenizer.tokenize(sent)
    src_tokenized = sent

    # translate_sentence
    p = xmlrpclib.ServerProxy("http://localhost:8080/RPC2")
    translation = p.translate({ "sent": sent, "align": True })
    align = parse_align(sent, translation['sent'], translation['align'])
    sent = translation['sent']

    # recase
    r = xmlrpclib.ServerProxy("http://localhost:9000/RPC2")
    sent = r.translate({ "sent": sent })['sent']
    tgt_tokenized = ' '.join(sent.split())

    # detokenize
    if do_detok:
        detokenizer = Detokenizer()
        sent = detokenizer.detokenize(sent)

    r1 = { 'sent': sent.strip(), 'score': 100, 'rank': 0 }
    if doalign:
##  'alignment': align,
        r1 = dict(r1.items() +
                  {
                   'src-tokenized': src_tokenized,
                   'tgt-tokenized': tgt_tokenized,
                   'alignment-raw': add_tgt_end(translation['align'],
                                                tgt_tokenized),
                   }.items())
    return r1


def process_task(task):
    """\
    Main entry point for translation. Process the task specified in a dict
    and return the results.
    """
    # language settings are ignored, for now
    #f = task['sourceLang']
    #e = task['targetLang']

    # obtain text and settings 
    text = task['text']
    do_align = task.get('alignmentInfo', '').lower() == 'true'
    do_detok = task.get('detokenize', 'true').lower() == 'true'
    return {
        'translation': [
        {
            # generate id
            "translationId": uuid.uuid4().hex,
            # run the translation
            "translated": translate_paragraph(text, do_align, do_detok),
        }
        ]
    }


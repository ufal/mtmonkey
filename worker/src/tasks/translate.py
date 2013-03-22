#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import uuid
import xmlrpclib
from subprocess import Popen, PIPE
import operator
import os

SCRIPT_PATH = os.path.split(os.path.dirname(__file__))[0] + '/perl-scripts/'

def ex(text):
  return text + text[-1]

def paragraph(text, doalign):
  if not text:
    return [""]
  t = text.strip()
  if not t:
    return [""]
  t_utf8 = t.encode('utf-8')
  p = Popen([SCRIPT_PATH + 'split-sentences.pl', '-l en'], stdin=PIPE, stdout=PIPE, stderr=None)
  (out, stderr) = p.communicate(ex(t).encode('utf-8'))
  p.stdin.close()
  try: p.kill()
  except Exception, e: pass
  #
  lines = filter(None, out.split('\n'))
  return [translate(l, doalign) for l in lines]

def parse_align(orig, transl, align):
  p = orig.split()
  b = [' '.join(p[a['src-start']:a['src-end']+1]) for a in align]

  o = transl.split()
  oi = sorted([int(w['tgt-start']) for w in align])
  oi.append(len(o)+1)
  a = [' '.join(o[oi[x]:oi[x+1]]) for x in xrange(len(oi)-1)]

  return zip(a, b)

def add_tgt_end(align, tgttok):
  ks = map(lambda x: x['tgt-start'], align)
  n = len(tgttok.split())
  ks.append(n)
  for i in xrange(len(align)):
    align[i]['tgt-end'] = ks[i+1]-1
  return align

def translate(text, doalign):
  # tokenize
  p = Popen([SCRIPT_PATH + 'tokenizer.pl', '-l', 'en'],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
  (text, stderr) = p.communicate((text.lower()))
  src_tokenized = ' '.join(text.split())
  p.stdin.close()
  try: p.kill()
  except Exception, e: pass

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
  p = Popen([SCRIPT_PATH + 'detokenizer.pl', '-l', 'en'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
  (text, stderr) = p.communicate(text.encode('utf-8'))
  p.stdin.close()
  try: p.kill()
  except Exception, e: pass

  r1 = { 'text': text.strip().decode("utf8"), 'score': 100, 'rank': 0 }
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
  a = ('alignmentInfo' in task) and (task['alignmentInfo']=='true')
  return {
    'translation': [
    {
      "translationId": uuid.uuid4().hex,
      "translated": paragraph(t, a),
    }
    ]
  }

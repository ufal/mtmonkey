#!/usr/bin/env python

import time
import uuid
import xmlrpclib
import operator
import os
from util.morphodita import Morphodita
from util.normalize_english import EnglishNormalizer
from util.tokenize import Tokenizer
from util.detokenize import Detokenizer
from util.split_sentences import SentenceSplitter

class Translator(object):
    """Base class for all classes that handle the 'translate' task for MTMonkeyWorkers"""

    def __init__(self):
        pass

    def process_task(self, task):
        raise NotImplementedError()


class StandaloneTranslator(Translator):
    """This handles the 'translate' task via an XML-RPC server that is able to do
    all parts of the translation process by itself."""

    def __init__(self, translate_port, url_path, src_key, tgt_key, transl_setting):
        """Store all translation server settings.

        @param translate_port: the port on which the server operates (localhost assumed)
        @param url_path: the URL path to the translation service
        @param src_key: the dictionary key under which the source text is expected in the request
        @param tgt_key: the dictionary key where the translation appears in the response
        @param transl_setting: other (unchanging) settings to be passed to the server
        """
        self.translate_proxy_addr = "http://localhost:" + translate_port + url_path
        self.transl_setting = transl_setting
        self.src_key = src_key
        self.tgt_key = tgt_key

    def process_task(self, task):
        """Just translating, ignoring all possible options."""
        # translate the text
        translate_proxy = xmlrpclib.ServerProxy(self.translate_proxy_addr)
        transl_input = {}
        transl_input.update(self.transl_setting)
        transl_input[self.src_key] = task['text']
        translation = translate_proxy.translate(transl_input)
        import sys
        print >> sys.stderr, translation
        translation = translation[self.tgt_key]
        # TODO add support for n-best etc. if the server supports them in any way
        # (general API translation?)

        # construct the resulting JSON (if the translation fails, the Exception will not be caught)
        result = {'translation': [{'translated': [{'text': translation,
                                                   'score': 100,
                                                   'rank': 0}],
                                   'translationId': uuid.uuid4().hex}], }
        return result


class MosesTranslator(Translator):
    """Handles the 'translate' task for MTMonkeyWorkers using Moses XML-RPC servers
    and built-in segmentation, tokenization, and detokenization.
    """

    def __init__(self, translate_port, recase_port, source_lang, target_lang, morphodita_model):
        """Initialize a MosesTranslator object according to the given 
        configuration settings.
        
        @param translate_port: the port at which the Moses translator operates
        @param recase_port: the port at which the recaser operates
        @param source_lang: source language (ISO-639-1 ID)
        @param target_lang: target language (ISO-639-1 ID)
        """
        # precompile XML-RPC Moses server addresses
        self.translate_proxy_addr = "http://localhost:" + translate_port + "/RPC2"
        self.recase_proxy_addr = None
        if recase_port is not None:
            self.recase_proxy_addr = "http://localhost:" + recase_port + "/RPC2"

        # initialize text processing tools (can be shared among threads)
        self.splitter = SentenceSplitter({'language': source_lang})
        self.normalizer = EnglishNormalizer()
        self.tokenizer = Morphodita(morphodita_model)
        self.detokenizer = Detokenizer({'moses_deescape': True,
                                        'capitalize_sents': True,
                                        'language': target_lang})


    def process_task(self, task):
        """Process translation task. Splits request into sentences, then translates and
        recases each sentence."""
        # check parameters
        # be lenient and allow anything that can map to a boolean for alignmentInfo and detokenize
        doalign = _convert_boolean(task.get('alignmentInfo', ''), False)
        dodetok = _convert_boolean(task.get('detokenize', ''), True)
        dotok = _convert_boolean(task.get('tokenize', ''), True)
        dosegment = _convert_boolean(task.get('segment', ''), True)

        nbestsize = min(task.get('nBestSize', 1), 10)

        # run the translation
        src_lines = self.splitter.split_sentences(task['text']) if dosegment else [ task['text'] ]
        ret_src_tok = doalign or len(src_lines) > 1
        translated = [self._translate(line, doalign, dodetok, nbestsize, ret_src_tok, dotok, dosegment) for line in src_lines]
        return {
            'translationId': uuid.uuid4().hex,
            'translation': translated
        }

    def _translate(self, src, doalign, dodetok, nbestsize, ret_src_tok, dotok, dosegment):
        """Translate and recase one sentence. Optionally, word alignment
        between source and target is included on the output.

        @param src: source text (one sentence).
        @param dodetok: detokenize output?
        @param nbestsize: size of n-best lists on the output
        @param ret_src_tok: return tokenized source sentences?
        """

        # create server proxies (needed for each thread)
        translate_proxy = xmlrpclib.ServerProxy(self.translate_proxy_addr)
        recase_proxy = None
        if self.recase_proxy_addr is not None:  # recasing only if there is a recaser set up
            recase_proxy = xmlrpclib.ServerProxy(self.recase_proxy_addr)

        # tokenize
        src_norm = self.normalizer.normalize(src)
        src_tokenized = self.tokenizer.tokenize(src_norm, True, True) if dotok else src_norm

        # translate
        translation = translate_proxy.translate({
            "text": src_tokenized,
            "align": doalign,
            "nbest": nbestsize,
            "nbest-distinct": True,
        })

        # provide n-best lists
        rank = 0
        hypos = []
        for hypo in translation['nbest']:
            # recase (if there is a recaser set up)
            if recase_proxy is not None:
                recased = recase_proxy.translate({"text": hypo['hyp']})['text'].strip()
            else:
                recased = hypo['hyp']

            # construct the output
            parsed_hypo = {
                'text': recased,
                'score': hypo['totalScore'],
                'rank': rank,
            }
            if dodetok:  # detokenize if needed
                parsed_hypo['text'] = self.detokenizer.detokenize(recased)

            if doalign:  # provide alignment information if needed
                parsed_hypo['tokenized'] = recased
                parsed_hypo['alignment-raw'] = _add_tgt_end(hypo['align'], recased)

            rank += 1
            hypos.append(parsed_hypo)

        result = {
            'src': src,
            'translated': hypos,
        }

        if ret_src_tok:
            result['src-tokenized'] = src_tokenized

        return result

def _add_tgt_end(align, tgttok):
    ks = map(lambda x: x['tgt-start'], align)
    n = len(tgttok.split())
    ks.append(n)
    for i in xrange(len(align)):
        align[i]['tgt-end'] = ks[i + 1] - 1
    return align

def _backward_transform(result, doalign, dodetok):
    """Transform the produced output structure to old format.
    Deprecated - do not use anymore."""
    translation = []
    min_nbest_length = min([len(s['translated']) for s in result['sentences']])
    for rank in range(0, min_nbest_length):
        translated = []
        for sent in result['sentences']:
            oldformat = {}
            if dodetok:
                oldformat['src-tokenized'] = sent['src-tokenized']

            oldformat['text'] = sent['translated'][rank]['text']
            oldformat['rank'] = rank
            oldformat['score'] = sent['translated'][rank]['score']
            if doalign:
                oldformat['tgt-tokenized'] = sent['translated'][rank]['tokenized']
                oldformat['alignment-raw'] = sent['translated'][rank]['alignment-raw']

            translated.append(oldformat)

        translation.append({'translated': translated, 'translationId': result['translationId']})

    return { 'translation': translation }

def _convert_boolean(value, default):
    if unicode(value).lower() in ['false', 'f', 'no', 'n', '0']:
        return False
    elif unicode(value).lower() in ['true', 't', 'yes', 'y', '1']:
        return True
    else:
        return default

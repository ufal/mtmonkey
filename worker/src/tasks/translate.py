#!/usr/bin/env python

import time
import uuid
import xmlrpclib
import operator
import os
import logging as logger
from util.parallel import parallel_map
from util.tokenize import Tokenizer
from util.detokenize import Detokenizer
from util.split_sentences import SentenceSplitter

from util.preprocessor import Tokenizer as PerlTokenizer
from util.preprocessor import Detokenizer as PerlDetokenizer
from util.preprocessor import Truecaser
from util.preprocessor import Detruecaser
from util.preprocessor import Normalizer
from util.preprocessor import CompoundSplitter

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
    @ivar translate_proxy_addr: proxy address for the translation server
    @ivar recase_proxy_addr: proxy address for the recaser-decoder server
    @ivar splitter: the sentence splitter class to be used along all threads
    @type splitter: SentenceSplitter
    @ivar preprocessors: a list of pre-processing classes supporting the function 
    "process_string" to run before text is sent to the decoder
    @ivar postprocessors: a list of post-processing classes to run after text is 
    sent to the decoder
    @ivar threads: desired number of threads
    @type threads: int
    """

    def __init__(self, translate_port, recase_port, source_lang, target_lang, threads, truecaser_model=None, splitter_model=None, perl_tokenizer=None, normalizer=None):
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
        if recase_port is not None and recase_port.strip() != "":
            self.recase_proxy_addr = "http://localhost:" + recase_port + "/RPC2"

        # initialize text processing tools (can be shared among threads)
        self.splitter = SentenceSplitter({'language': source_lang})
        # put sentence-level pre- and post-processors in two lists
        # depending on whether they are enabled from the settings
        self.preprocessors = []
        self.postprocessors = []
        if normalizer:
            normalizer = Normalizer(source_lang)
            self.preprocessors.append(normalizer)
        if not perl_tokenizer:
            tokenizer = Tokenizer({'lowercase': True,
                                    'moses_escape': True})
            self.preprocessors.append(tokenizer)
            detokenizer = Detokenizer({'moses_deescape': True,
                                        'capitalize_sents': True,
                                        'language': target_lang}) 
            self.postprocessors.append(detokenizer)
        else:
            tokenizer = PerlTokenizer(source_lang)
            self.preprocessors.append(tokenizer)
            detokenizer = PerlDetokenizer(target_lang)
            self.postprocessors.append(detokenizer)
        if truecaser_model:
            truecaser = Truecaser(source_lang, truecaser_model)
            self.preprocessors.append(truecaser)
            detruecaser = Detruecaser(target_lang)
            self.postprocessors.append(detruecaser)
        if splitter_model:
            compound_splitter = CompoundSplitter(source_lang, splitter_model)
            self.preprocessors.append(compound_splitter)

        #post-processors to run in the opposite order as pre-processors
        self.postprocessors.reverse()

        self.threads = threads


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

        #def _translator(line):
        #    return self._translate(line, doalign, dodetok, nbestsize, ret_src_tok, dotok, dosegment)
        #
        #translated = parallel_map(_translator, src_lines)
        translated = []
        for line in src_lines:
            translated.append(self._translate(line, doalign, dodetok, nbestsize, ret_src_tok, dotok, dosegment))


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

        # preprocess
        src_original = src
        if dotok:
            for preprocessor in self.preprocessors:
                #logger.warning("Preprocessed source before {}: {}".format(preprocessor.__class__.__name__, src))
                src = preprocessor.process_string(src)
                #commented out as causing utf-8 errors    
                #logger.warning("Preprocessed source after {}: {}".format(preprocessor.__class__.__name__, src))
        # translate
        translation = translate_proxy.translate({
            "text": src,
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
                postprocessed = recase_proxy.translate({"text": hypo['hyp']})['text'].strip()
            else:
                postprocessed = hypo['hyp']

            # construct the output
            parsed_hypo = {
                'text': postprocessed,
                'text-unprocessed': hypo['hyp'],
                'score': hypo['totalScore'],
                'rank': rank,
            }
            if dodetok:  # postprocess if needed
                for postprocessor in self.postprocessors:
                    #logger.warning("Postprocessed output before {}: {}".format(postprocessor.__class__.__name__, postprocessed))
                    postprocessed = postprocessor.process_string(postprocessed)
                    #logger.warning("Postprocessed output after {}: {}".format(postprocessor.__class__.__name__, postprocessed))
            parsed_hypo['text'] = postprocessed
            if doalign:  # provide alignment information if needed
                parsed_hypo['tokenized'] = postprocessed
                parsed_hypo['alignment-raw'] = _add_tgt_end(hypo['align'], postprocessed)

            rank += 1
            hypos.append(parsed_hypo)

        result = {
            'src': src_original,
            'translated': hypos,
        }

        if ret_src_tok:
            result['src-tokenized'] = src

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

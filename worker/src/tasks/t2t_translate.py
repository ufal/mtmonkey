#!/usr/bin/env python
# encoding=utf8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import uuid
import operator
import os
import subprocess
import sys
from pprint import pprint
from util.parallel import parallel_map
from util.tokenize import Tokenizer
import numpy as np

from oauth2client.client import GoogleCredentials
from six.moves import input  # pylint: disable=redefined-builtin

from tensor2tensor import problems as problems_lib  # pylint: disable=unused-import
from tensor2tensor.serving import serving_utils
from tensor2tensor.utils import registry
from tensor2tensor.utils import usr_dir
import tensorflow as tf

reload(sys)
sys.setdefaultencoding('utf8')

class Translator(object):
    """Base class for all classes that handle the 'translate' task for MTMonkeyWorkers"""

    def __init__(self):
        pass

    def process_task(self, task):
        raise NotImplementedError()


class TransformerTranslator(Translator):
    """Handles the 'translate' task for MTMonkeyWorkers using Moses XML-RPC servers
    and built-in segmentation, tokenization, and detokenization.
    """

    def __init__(self, translate_host, translate_port, source_lang, target_lang, model_name, problem, t2t_usr_dir, data_dir, preprocess_cmd, postprocess_cmd):
        """Initialize a TransformerTranslator object according to the given 
        configuration settings.
        
        @param translate_port: the port at which the Moses translator operates
        @param recase_port: the port at which the recaser operates
        @param source_lang: source language (ISO-639-1 ID)
        @param target_lang: target language (ISO-639-1 ID)
        @param preprocess_cmd: bash command for text preprocessing
        @param postprocess_cmd: bash command for text posprocessing
        """
        # precompile Tensorflow server addresses
        self.server = translate_host + ":" + translate_port

        # initialize text processing tools (can be shared among threads)
        self.tokenizer = Tokenizer({'lowercase': True,
                                    'moses_escape': True})
        self.preprocess = preprocess_cmd
        self.postprocess = postprocess_cmd
        usr_dir.import_usr_dir(t2t_usr_dir)
        self.problem = registry.problem(problem)
        hparams = tf.contrib.training.HParams(
            data_dir=os.path.expanduser(data_dir))
        self.problem.get_hparams(hparams)
        self.request_fn = serving_utils.make_grpc_request_fn(
            servable_name=model_name,
            server=self.server,
            timeout_secs=30)

    def process_task(self, task):
        """Process translation task. Splits request into sentences, then translates and
        recases each sentence."""
        # check parameters
        # be lenient and allow anything that can map to a boolean for alignmentInfo and detokenize
        dodetok = _convert_boolean(task.get('detokenize', ''), True)
        dotok = _convert_boolean(task.get('tokenize', ''), True)
        dosegment = _convert_boolean(task.get('segment', ''), True)

        # run the translation
        def _translator(text):
            return self._translate(text, dodetok, dotok, dosegment)

        translated, score = _translator(task['text'])

        result = {'translation': [{'translated': [{'text': translated,
                                                   'score': score,
                                                   'rank': 0}],
                                   'translationId': uuid.uuid4().hex}], }
        return result

    def _translate(self, src, dodetok, dotok, dosegment):
        """Translate one sentence. 

        @param src: source text (one sentence).
        @param dodetok: detokenize output?
        @param ret_src_tok: return tokenized source sentences?
        @param dotok: tokenize output?
        """
        def _prepare_cmd(cmd, inputValue="", outputValue=""):
            SPACE_SPLIT_ELEMENT="SPACE_SPLIT_ELEMENT"
            cmd_args = cmd.replace(" ", SPACE_SPLIT_ELEMENT).replace('"$input"', inputValue).replace('"$output"', outputValue)
            return cmd_args.split(SPACE_SPLIT_ELEMENT)

        def _run_cmd(*args):
            try:
                out = subprocess.check_output(args[0]).strip()                       
                return 0, out
            except subprocess.CalledProcessError as grepexc:                                                                                                   
                return grepexc.returncode, grepexc.output

        # tokenize
        src_tokenized = self.tokenizer.tokenize(src) if dotok else src

        if (self.preprocess):
            cmd_args = _prepare_cmd(self.preprocess, src)
            (cmd_error, cmd_output) = _run_cmd(cmd_args)
            if (cmd_error == 0):
                src_tokenized = cmd_output
            else:
                sys.stderr.write("{0}\n{1}".format(cmd_error, cmd_output))
        
        # translate
        outputs = serving_utils.predict([src_tokenized], self.problem, self.request_fn)
        outputs, = outputs
        result, score = outputs

        if (self.postprocess):
            cmd_args = _prepare_cmd(self.postprocess, src, result)
            (cmd_error, cmd_output) = _run_cmd(cmd_args)
            if (cmd_error == 0):
                result = cmd_output
            else:
                 sys.stderr.write("{0}\n{1}".format(cmd_error, cmd_output))

        result = {
            'src': src,
            'translated': result
        }, score.item()

        return result

def _convert_boolean(value, default):
    if unicode(value).lower() in ['false', 'f', 'no', 'n', '0']:
        return False
    elif unicode(value).lower() in ['true', 't', 'yes', 'y', '1']:
        return True
    else:
        return default

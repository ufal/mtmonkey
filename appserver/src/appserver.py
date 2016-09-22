#!/usr/bin/env python

import json
import os
import logging
import validictory
import xmlrpclib
import requests
import getopt
import sys
from collections import defaultdict
from threading import Lock
from flask import Flask, request, abort, Response
from socket import error as socket_err

class JsonProxy(object):
    """A simple proxy that sends JSON-encoded requests to workers over HTTP."""

    def __init__(self, addr):
        self.addr = addr

    def process_task(self, task):
        r = requests.post(self.addr, data=json.dumps(task), headers={'content-type': 'application/json'})
        return r.json()

class WorkerNotFoundException(Exception): pass

class WorkerCollection:
    """Collection of MT workers; provides thread-safe round-robin selection among
    available workers."""

    def __init__(self, workers):
        # initialize list of workers
        self._workers = defaultdict(list)
        for pair_id, workers_list in workers.items():
            for worker_desc in workers_list:
                self.add(pair_id, worker_desc)

        # initialize next worker numbers
        self.nextworker = dict((pair_id, 0) for pair_id in workers)
        self.lock = Lock()

    def add(self, pair_id, worker_desc):
        # is worker type directly specified
        if ' ' in worker_desc:
            worker_type, worker_addr = worker_desc.split(' ')
        else:
            worker_type = 'xml' # default to XML workers (original MTMonkey)
            worker_addr = worker_desc

        worker_addr = self._normalize_url(worker_addr)

        # JSON workers use JsonProxy, XML-RPC workers use xmlrpclib
        proxy_cls = JsonProxy if worker_type == 'json' else xmlrpclib.ServerProxy

        # add our worker
        self._workers[pair_id].append((worker_addr, proxy_cls))

    def get(self, pair_id):
        """Get a worker for the given language pair"""
        if not pair_id in self.workers:
            raise WorkerNotFoundException
        with self.lock:
            worker_id = self.nextworker[pair_id]
            self.nextworker[pair_id] = (worker_id + 1) % len(self._workers[pair_id])
            return self._workers[pair_id][worker_id]

    def keys(self):
        return self._workers.keys()

    # normalize worker URL to include "http://" and "/"
    def _normalize_url(self, url):
        if not url.startswith('http'):
            url = 'http://' + url
        if not url.endswith('/'):
            url += '/'
        return url

class MTMonkeyService:
    """MTMonkey web service; calls workers which process individual language pairs
    and returns their outputs in JSON"""

    def __init__(self, workers, logger, passphrase):
        self.workers = workers
        self.logger = logger
        self._passphrase = passphrase

        # initialize list of supported systemIds per pair
        self.systems_for_pair = {}
        for pair_id in workers.keys():
            system_id = ''
            if '.' in pair_id:
                pair_id, system_id = pair_id.split('.', 1)
            if not pair_id in self.systems_for_pair:
                self.systems_for_pair[pair_id] = set()
            self.systems_for_pair[pair_id].add(system_id)
        self.logger.info(self.systems_for_pair)

    def post(self):
        """Handle POST requests"""
        if not request.json:
            abort(400)
        self.logger.info('Received new task [POST]')
        result = self._dispatch_task(request.json)
        return self._wrap_result(result)

    def get(self):
        """Handle GET requests"""
        args = request.args.to_dict()
        args['action'] = 'translate'

        # required type conversions (GET doesn't have any notion of types)
        if 'nBestSize' in args:
            args['nBestSize'] = int(args['nBestSize'])
        if 'alignmentInfo' in args:
            args['alignmentInfo'] = self._convert_boolean(args['alignmentInfo'], False)
        if 'detokenize' in args:
            args['detokenize'] = self._convert_boolean(args['detokenize'], True)
        if 'tokenize' in args:
            args['tokenize'] = self._convert_boolean(args['tokenize'], True)
        if 'segment' in args:
            args['segment'] = self._convert_boolean(args['segment'], True)

        result = self._dispatch_task(args)
        self.logger.info('Received new task [GET]')
        return self._wrap_result(result)
    
    def worker_api(self):
        """Handle POST requests from worker nodes"""

        # is this valid JSON
        if not request.json:
            abort(400)

        # does the JSON conform to our schema
        try:
            validictory.validate(request.json, MTMonkeyService._worker_api_schema)
        except ValueError as e:
            return json.dumps({ "errorCode": 100, "errorMessage": str(e) })

        # are we configured to handle worker API requests?
        if not self._passphrase:
            return json.dumps({ "errorCode": 101, "errorMessage": "server does not allow worker API" })

        # authenticate the worker using passphrase
        if request.json['passPhrase'] != self._passphrase:
            return json.dumps({ "errorCode": 102, "errorMessage": "invalid passphrase" })

        # everything is fine, what action is this?
        if request.json['action'] == 'register':
            # add a new worker to our collection, TODO do not allow duplicate entries
            addr = request.remote_addr
            port = request.json['realPort']
            src_lang = request.json['sourceLang']
            tgt_lang = request.json['targetLang']
            self.workers.add(src_lang + "-" + tgt_lang, addr.rstrip('/') + ":" + str(port))
            return json.dumps({ "errorCode": 0 })
        else:
            return json.dumps({ "errorCode": 103, "errorMessage": "unsupported action: " + request.json['action'] })

    def _dispatch_task(self, task):
        """Dispatch task to worker and return its output (and/or error code)"""
        pair_id = "%s-%s" % (task['sourceLang'], task['targetLang'])
        if 'systemId' in task:
            pair_id += '.' + task['systemId']

        # validate the task
        try:
            validictory.validate(task, MTMonkeyService._public_api_schema)
        except ValueError as e:
            return { "errorCode": 5, "errorMessage": str(e) }

        # acquire a worker
        try:
            worker_addr, worker_proxy_class = self.workers.get(pair_id)
        except WorkerNotFoundException:
            self.logger.warning("Requested unknown language pair/system ID" + pair_id)
            system_id = ''
            if '.' in pair_id:
                pair_id, system_id = pair_id.split('.', 1)
            if pair_id not in self.systems_for_pair:
                err_msg = "Language pair not supported: " + pair_id
            else:
                err_msg = "Invalid systemId '%s' for %s." % (system_id, pair_id)
                err_msg += " Available: '%s'." % "', '".join(self.systems_for_pair[pair_id])
            return {
                "errorCode": 3,
                "errorMessage": err_msg
            }

        # call the worker
        worker_proxy = worker_proxy_class(worker_addr)
        try:
            result = worker_proxy.process_task(task)
        except (socket_err, xmlrpclib.Fault,
                xmlrpclib.ProtocolError, xmlrpclib.ResponseError) as e:
            self.logger.error("Call to worker %s failed: %s" % (worker_addr, task))
            return {
                "errorCode": 1,
                "errorMessage": str(e)
            }

        # check for errors returned by worker (default worker error code: 8, may be overridden)
        errorMessage = result.get('error', result.get('errorMessage'))
        if errorMessage not in [None, '', 'OK']:
            return {
                "errorCode": result.get('errorCode', 8),
                "errorMessage": errorMessage
            }

        # OK, return output of the worker
        result["errorCode"] = 0
        result["errorMessage"] = "OK"
        return result

    def _wrap_result(self, result):
        """Wrap the output in JSON and fix old API"""

        # When the input text contains more sentences, translation of each has a separate structure.
        # The old API used result["translation"][NBESTLIST_N]["translated"][SENTENCE_NUMBER]
        # The new API uses result["translation"][SENTENCE_NUMBER]["translated"][NBESTLIST_N]
        # See https://github.com/ufal/mtmonkey/blob/master/API.md
        # So let's detect the old API and convert it to the new API
        # to allow backward compatibility with old workers (possibly not MT-Monkey-based).
        if ("translation" in result and len(result["translation"]) == 1
                and "translated" in result["translation"][0]):

            translated = result["translation"][0]["translated"]
            if len(translated) > 1 and all(i["rank"] == 0 for i in translated):
                newtranslation = [{"translated": [i, ], "src-tokenized": i["src-tokenized"]}
                                  for i in translated]
                for x in newtranslation:
                    del x["translated"][0]["src-tokenized"]
                result["translation"] = newtranslation

        return Response(json.dumps(result, encoding='utf-8',
                                   ensure_ascii=False, indent=4),
                        mimetype='application/javascript')

    def _convert_boolean(self, value, default):
        if value.lower() in ['false', 'f', 'no', 'n', '0']:
            return False
        elif value.lower() in ['true', 't', 'yes', 'y', '1']:
            return True
        else:
            return default

    _public_api_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "userId": {"type": "string", "required": False},
            "sourceLang": {"type": "string"},
            "targetLang": {"type": "string"},
            "systemId": {"type": "string", "required": False},
            "text": {"type": "string"},
            "nBestSize": {"type": "integer", "required": False},
            "detokenize": {"type": ['boolean', 'string', 'integer'], "required": False},
            "tokenize": {"type": ['boolean', 'string', 'integer'], "required": False},
            "segment": {"type": ['boolean', 'string', 'integer'], "required": False},
            "alignmentInfo": {"type": ['boolean', 'string', 'integer'], "required": False},
            "docType": {"type": "string", "required": False},
            "profileType": {"type": "string", "required": False},
        },
    }

    _worker_api_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "sourceLang": {"type": "string"},
            "targetLang": {"type": "string"},
            "realPort": {"type": "integer"},
            "passPhrase": {"type": "string"},
        },
    }

#
# main
#

def main():
    # Create Flask app
    app = Flask(__name__)

    # Initialize logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(message)s")
    logger = logging.getLogger('server')

    # load config
    try:
        app.config.from_pyfile('appserver.cfg')
        logger.info("Loaded config from file appserver.cfg")
    except:
        pass

    # read command-line options
    opts, args = getopt.getopt(sys.argv[1:], 'c:')
    for opt, arg in opts:
        if opt == '-c':
            # Overwrite default settings
            app.config.from_pyfile(arg)
            logger.info("Loaded config from file " + arg)
        else:
            logger.error("Unknown command-line option: " + opt)

    # passphrase to identify authorized workers
    passphrase = app.config.get('PASSPHRASE')
    if passphrase:
        logger.info("passphrase specified, will accept worker API requests")
    else:
        logger.info("no passphrase given, worker API will not be available")

    # initialize workers collection
    workers = WorkerCollection(app.config['WORKERS'])

    # initialize MTMonkey service
    mtmonkey = MTMonkeyService(workers, logger, passphrase)

    # register routes
    app.route(app.config['URL'], methods=['POST'])(mtmonkey.post)
    app.route(app.config['URL'])(mtmonkey.get)
    app.route(app.config['URL'] + "/worker-api", methods=['POST'])(mtmonkey.worker_api)

    # run
    app.run(host="", port=app.config['PORT'], threaded=True)

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import json
import os
import logging
import validictory
import xmlrpclib
from threading import Lock
from flask import Flask, request, abort, Response
from socket import error as socket_err

class WorkerNotFoundException(Exception): pass

class WorkerCollection:
    """Collection of MT workers; provides thread-safe round-robin selection among
    available workers."""

    def __init__(self, workers):
        self.workers = workers
        self.nextworker = dict((pair_id, 0) for pair_id in workers)
        self.lock = Lock()

    def get(self, pair_id):
        """Get a worker for the given language pair"""
        if not pair_id in self.workers:
            raise WorkerNotFoundException
        with self.lock:
            worker_id = self.nextworker[pair_id]
            self.nextworker[pair_id] = (worker_id + 1) % len(self.workers[pair_id])
            return self.workers[pair_id][worker_id]

class KhresmoiService:
    """Khresmoi web service; calls workers which process individual language pairs
    and returns their outputs in JSON"""

    def __init__(self, workers, logger):
        self.workers = workers
        self.logger  = logger

    def post(self):
        """Handle POST requests"""
        if not request.json:
            abort(400)
        self.logger.info('Received new task [POST]')
        result = self._dispatch_task(request.json)
        return self._wrap_result(result)
    
    def get(self):
        """Handle GET requests"""
        result = self._dispatch_task({
            'action': 'translate',
            'sourceLang': request.args.get('sourceLang', None),
            'targetLang': request.args.get('targetLang', None),
            'text': request.args.get('text', None)
        })
        self.logger.info('Received new task [GET]')
        return self._wrap_result(result)

    def _dispatch_task(self, task):
        """Dispatch task to worker and return its output (and/or error code)"""
        pair_id = "%s-%s" % (task['sourceLang'], task['targetLang'])
    
        # validate the task
        try:
            self._validate(task)
        except ValueError as e:
            return { "errorCode": 5, "errorMessage": str(e) }
    
        # acquire a worker
        try:
            worker = self.workers.get(pair_id)
        except WorkerNotFoundException:
            self.logger.warning("Requested unknown language pair " + pair_id)
            return {
                "errorCode": 6,
                "errorMessage": "Language pair not supported: " + pair_id
            }
    
        # call the worker
        worker_proxy = xmlrpclib.ServerProxy("http://" + worker + "/")
        try:
            result = worker_proxy.process_task(task)
        except (socket_err, xmlrpclib.Fault,
                xmlrpclib.ProtocolError, xmlrpclib.ResponseError) as e:
            self.logger.error("Call to worker %s failed: %s" % (worker, task))
            return {
                "errorCode": 7,
                "errorMessage": str(e)
            }
    
        # OK, return output of the worker
        result["errorCode"] = 0
        result["errorMessage"] = "OK"
        return result
    
    def _wrap_result(self, result):
        """Wrap the output in JSON"""
        return json.dumps(result, encoding='utf-8', ensure_ascii=False, indent=4)
        
    def _validate(self, task):
        """Validate task according to schema"""
        schema = {
            "type": "object",
            "properties": {
                "action": {"type": "string"},
                "userId": {"type": "string", "required": False},
                "sourceLang": {"type": "string"},
                "targetLang": {"type": "string"},
                "text": {"type": "string"},
                "nBestSize": {"type": "integer", "required": False},
                "alignmentInfo": {"type": "string", "required": False},
                "docType": {"type": "string", "required": False},
                "profileType": {"type": "string", "required": False},
            },
        }
        validictory.validate(task, schema)

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
    
    # Overwrite default settings by envvar
    try:
        app.config.from_envvar('MICROTASK_SETTINGS')
        logger.info("Loaded config from file " + os.environ['MICROTASK_SETTINGS'])
    except:
        pass

    # initialize workers collection
    workers = WorkerCollection(app.config['WORKERS'])  

    # initialize Khresmoi service
    khresmoi = KhresmoiService(workers, logger)

    # register routes
    app.route('/khresmoi', methods=['POST'])(khresmoi.post)
    app.route('/khresmoi')(khresmoi.get)

    # run
    app.run(host=app.config['HOST'], port=app.config['PORT'], threaded=True)

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import json
import logging
import validictory
import xmlrpclib
from threading import Lock
from flask import Flask, request, abort, Response
from socket import error as socket_err

# Create Flask app
app = Flask(__name__)
app.config.from_pyfile('server.cfg')

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger('server')

# Overwrite default settings by envvar
try:
    app.config.from_envvar('MICROTASK_SETTINGS')
except:
    pass

class WorkerNotFoundException(Exception): pass

class WorkerCollection:
    def __init__(self, workers):
        self.workers = workers
        self.nextworker = dict((pair_id, 0) for pair_id in workers)
        self.lock = Lock()

    """Get a worker for the given language pair, do round-robin selection when
    more than one worker provides the language pair"""
    def get(self, pair_id):
        if not pair_id in self.workers:
            raise WorkerNotFoundException
        with self.lock:
            worker_id = self.nextworker[pair_id]
            self.nextworker[pair_id] = (worker_id + 1) % len(self.workers[pair_id])
            return self.workers[pair_id][worker_id]

workers = WorkerCollection(app.config['WORKERS'])

def dispatch_task(task):
    pair_id = "%s-%s" % (task['sourceLang'], task['targetLang'])

    # validate the task
    try:
        validate(task)
    except ValueError as e:
        return { "errorCode": 5, "errorMessage": str(e) }

    # acquire a worker
    try:
        worker = workers.get(pair_id)
    except WorkerNotFoundException:
        logger.warning("Requested unknown language pair " + pair_id)
        return {
            "errorCode": 6,
            "errorMessage": "Language pair not supported: " + pair_id
        }

    # call the worker
    print "WORKER: ", worker
    worker_proxy = xmlrpclib.ServerProxy("http://" + worker)
    try:
        result = worker_proxy.process_task(task)
    except (socket_err, xmlrpclib.Fault,
            xmlrpclib.ProtocolError, xmlrpclib.ResponseError) as e:
        logger.error("Call to worker %s failed: %s" % (worker, task))
        return {
            "errorCode": 7,
            "errorMessage": str(e)
        }

    # OK, return output of the worker
    result["errorCode"] = 0
    result["errorMessage"] = "OK"
    return result

def wrap_result(result):
    return json.dumps(result, encoding='utf-8', ensure_ascii=False, indent=4)

#
# routes
#

@app.route('/khresmoi', methods=['POST'])
def khresmoi_post():
    if not request.json:
        abort(400)
    logger.info('Received new task [POST]')
    result = dispatch_task(request.json)
    return wrap_result(result)

@app.route('/khresmoi')
def khresmoi_get():
    result = dispatch_task({
        'action': 'translate',
        'sourceLang': request.args.get('sourceLang', None),
        'targetLang': request.args.get('targetLang', None),
        'text': request.args.get('text', None)
    })
    logger.info('Received new task [GET]')
    return wrap_result(result)

def validate(task):
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

if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'], threaded=True)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import anydbm
import urllib2
import urlparse
import json
import logging
import os

from flask import Flask, request, jsonify, abort
from random import choice
from tasks import hello, wait, translate

# Logging initialization
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger('microtask')

# Create Flask app
app = Flask(__name__)
try:
    app.config.from_pyfile('worker.cfg')
    logger.info('Loaded app config from %s' % 'worker.cfg')
except:
    logger.info('Could not load app config from %s' % 'worker.cfg')
    pass

# Overwrite default settings by envvar
try:
    app.config.from_envvar('MICROTASK_SETTINGS')
    logger.info('Loaded app config from %s' % os.getenv('MICROTASK_SETTINGS', '<undef>'))
except:
    logger.info('Could not load app config from %s' % os.getenv('MICROTASK_SETTINGS', '<undef>'))
    pass

# DBM for saving status
db = anydbm.open(app.config['DB'], 'c')
db['idle'] = '0'


###############################################################################
# Task processing
###############################################################################

def process_task_locally(task):
    """Dispatch tasks by their action"""
    # Run hello world task
    if task['action'] == 'hello':
        return hello.process_task(task)
    # Run wait task
    elif task['action'] == 'wait':
        return wait.process_task(task)
    elif task['action'] == 'translate':
        return translate.process_task(task)

def dispatch_task(task):
    """Process task locally, log progress."""
    # Process the task
    logger.info('Processing task "%s"' % task)
    try:
        result = process_task_locally(task)
    finally:
        db['idle'] = str(int(db['idle']) - 1)

    logger.info('Task finished')

    return result

###############################################################################
# Routes
###############################################################################

@app.route('/khresmoi', methods=['POST'])
def new_task():
    # Request must have type 'application/json'
    if request.json:
        logger.info('Received new task')
        result = dispatch_task(request.json)
        return jsonify(**result)
    else:
        abort(405)

@app.route('/idle-flip/<langs>')
def is_idle(langs):
    if not (langs in app.config['CAPA']):
        abort(405)
    db['idle'] = str(int(db['idle']) + 1)
    logger.info('Requested idle status, returning %s' % db['idle'])
    if db['idle'] == '1':
        return jsonify(idle=True)
    else:
        db['idle'] = str(int(db['idle']) - 1)
        return jsonify(idle=False)

@app.route('/idle-check')
def check_idle():
    logger.info('Requested idle status, returning %s' % db['idle'])
    return jsonify(capa=app.config['CAPA'], idle=db['idle'])

if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'], threaded=True)

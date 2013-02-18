#!/usr/bin/python
# -*- coding: utf-8 -*-

import anydbm
import urllib2
import urlparse
import json
import logging

from flask import Flask, request, jsonify, abort
from random import choice
from tasks import hello, wait, translate

# Create Flask app
app = Flask(__name__)
app.config.from_pyfile('worker.cfg')

# Logging initialization
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger('microtask')

# Overwrite default settings by envvar
try:
    app.config.from_envvar('MICROTASK_SETTINGS')
except:
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
    
    
###############################################################################
# Server methods
###############################################################################
    
def find_idle_slave():
    """Find first idle slave or pick randomly"""
    for slave in app.config['SLAVES']:
        # Create url for idle action
        slave_url = urlparse.urlunparse(('http', slave, 'idle-flip', '', '', ''))
        logger.info('Asking if %s is idle' % slave)
        
        # Send request and parse response (json)
        try:
            req = urllib2.Request(slave_url)
            response = urllib2.urlopen(req)
            result = json.loads(response.read())
        except urllib2.URLError, e:
            logger.error(e)
            abort(500)
        
        if result['idle']:
            logger.info('Server %s is idle' % slave)
            return slave
        else:
            logger.info('Server %s is busy' % slave)
            
    # All slaves are busy, choose random one
    return choice(app.config['SLAVES'])


def send_task_to_slave(task):
    """Send task to slave and wait for response"""
    # Choose one slave server and create its url
    slave_hostname = find_idle_slave()
    logger.info('Sendind task to %s' % slave_hostname)
    slave_url = urlparse.urlunparse(('http', slave_hostname, 'khresmoi', '', '', ''))

    # Create a new request from the task
    json_task = json.dumps(task)
    req_headers = {'Content-Type': 'application/json'}
    req = urllib2.Request(slave_url, headers=req_headers, data=json_task)

    # Send the request
    try:
        result = urllib2.urlopen(req)
    except urllib2.URLError, e:
        logger.error(e)
        abort(500)

    # Parse returned data
    result_data = json.loads(result.read())
    return result_data


def dispatch_task(task):
    """Send task to slave or process it"""
    # Check if this app is master
    if False:
        # Send the task to one of the slaves
        logger.info('Task will be sent to one of the slaves.')
        result = send_task_to_slave(task)
    else:
        # Process the task
        logger.info('Task will be processed locally')
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
    if not (langs in app.config['CAPA']): abort(405)
#        return jsonify(idle=False)
    # uprava
    #return jsonify(idle=True)
    ##
    db['idle'] = str(int(db['idle']) + 1)
    if db['idle'] == '1':
        return jsonify(idle=True)
    else:
        db['idle'] = str(int(db['idle']) - 1)
        return jsonify(idle=False)

if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'], threaded=True)

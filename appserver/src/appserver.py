#!/usr/bin/env python
# -*- coding: utf-8 -*-

import anydbm
import urllib2
import urlparse
import json
import logging
import validictory

from functools import wraps
from flask import Flask, request, jsonify, abort, Response
from random import choice, random
from tasks import hello, wait, translate
from time import sleep

# Create Flask app
app = Flask(__name__)
app.config.from_pyfile('appserver.cfg')

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

class WorkerNotFoundException(Exception): pass


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
    
def find_idle_slave(task):
    for slave in app.config['WORKERS']:
        # Create url for idle action
        langs = task['sourceLang'] + task['targetLang']
        slave_url = urlparse.urlunparse(('http', slave, 'idle-flip/%s' % langs, '', '', ''))
        logger.info('Asking if %s is idle, url=%s' % (slave, slave_url))
        
        for ntry in xrange(7):
          # Send request and parse response (json)
          try:
              req = urllib2.Request(slave_url)
              response = urllib2.urlopen(req)
              result = json.loads(response.read())
          except urllib2.URLError, e:
              logger.error(e)
              continue

          if result['idle']:
              logger.info('Server %s is idle' % slave)
              return slave
          else:
              logger.info('Server %s is busy (response: "%s")' %
                          (slave, result))
              sleep(ntry/2 + 1 + random())
            
    raise WorkerNotFoundException()
    # All slaves are busy, choose random one
    return choice(app.config['WORKERS'])


def send_task_to_slave(task):
    """Send task to slave and wait for response"""
    # Choose one slave server and create its url
    try:
        slave_hostname = find_idle_slave(task)
    except WorkerNotFoundException:
        return { "errorCode": 3,
                 "errorMessage": "No worker found."
        }
    logger.info('Sending task to %s' % slave_hostname)
    slave_url = urlparse.urlunparse(('http', slave_hostname, 'khresmoi', '', '', ''))

    # Create a new request from the task
    json_task = json.dumps(task)
    print json_task
    req_headers = {'Content-Type': 'application/json'}
    req = urllib2.Request(slave_url, headers=req_headers, data=json_task)

    # Send the request
    try:
        result = urllib2.urlopen(req)
    except urllib2.URLError, e:
        logger.error(e)
        abort(500)

    # Parse returned data
    txt = result.read()
    result_data = json.loads(txt)

    # Everything went fine
    result_data["errorCode"] = 0
    result_data["errorMessage"] = "OK"
    return result_data


def dispatch_task(task):
    """Send task to slave or process it"""
    # Check if this app is master
    if True:
        # Send the task to one of the slaves
        logger.info('Task will be sent to one of the slaves.')
        try:
            validate(task)
        except ValueError, e:
            return { "errorCode": 5, "errorMessage": str(e) }
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


###############################################################################
# Routes
###############################################################################

def check_auth(username, password):
    return username == "test" and password == "test123"

def authenticate():
    return Response(
    'Bad login or password or not used at all.\n'
    'You have to login with proper credentials.', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/khresmoi', methods=['POST'])
#@requires_auth
def khresmoi():
    return new_task()

@app.route('/khresmoi')
def khresmoi_get():
    return new_task_direct(
        request.args.get('sourceLang', None),
        request.args.get('targetLang', None),
        request.args.get('text', None))

#@app.route('/khresmoi-get-dev/<sourceLang>/<targetLang>/<text>')
#def khresmoi_get(sourceLang, targetLang, text):
#    return new_task_direct(sourceLang, targetLang, text)

def new_task():
    # Request must have type 'application/json'
    if request.json:
        logger.info('Received new task')
        result = dispatch_task(request.json)
        #return jsonify(**result)
        return json.dumps(result, encoding='utf-8', ensure_ascii=False, indent=4)
    else:
        abort(405)

def new_task_direct(sourceLang, targetLang, text):
    q = { 'action': 'translate', 'sourceLang': sourceLang, 'targetLang': targetLang, 'text': text }
    result = dispatch_task(q)
    return jsonify(**result)
        
@app.route('/idle-flip')
def is_idle():
    db['idle'] = str(int(db['idle']) + 1)
    if db['idle'] == '1':
        return jsonify(idle=True)
    else:
        db['idle'] = str(int(db['idle']) - 1)
        return jsonify(idle=False)

if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'], threaded=True)

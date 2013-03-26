#!/usr/bin/env python
# coding=utf-8

"""
Khresmoi MT tester. 

Usage:

    ./test.py [-h] <-w|-m> -p PORT
    
    -h = display this help
    -w = test if worker is running and able to process requests
    -m = test if Moses server is running
    -p = specify port number 
"""

from __future__ import unicode_literals
import sys
import getopt
import urllib2
import json
import logging
from random import random
from flask import jsonify

__author__ = "Ondřej Dušek"
__date__ = "2013"

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger('tester')

def test_moses(port):
    url = 'http://localhost:%d/RPC2' % port
    text = None
    try:
        logger.info('Testing %s ...' % url)
        r = xmlrpclib.ServerProxy(url)
        text = r.translate({ 'text': 'test' })['text']
    except (Exception, e):
        logger.info('Exception occurred: %s. Will return false.' % str(e))
        return False
    logger.info('Returned: %s' % text)
    return True if text else False


def test_worker(port):
    url = 'http://localhost:%d/idle-check' % port
    # Send idle check and parse response (JSON)
    for ntry in xrange(7):
      try:
          logger.info('Testing %s ...' % url)
          req = urllib2.Request(url)
          response = urllib2.urlopen(req)
          result = json.loads(response.read())
      except urllib2.URLError, e:
          continue
      # return true if worker is idle
      if result['idle']:
          logger.info('Worker is idle.')
          return True
      else:
          logger.info('Sleeping ...')
          sleep(ntry / 2 + 1 + random())
    # all trials ended with busy or error:
    logger.info('Failed: Worker is busy.')
    return False


def display_usage():
    """\
    Display program usage information.
    """
    print >> sys.stderr, __doc__


if __name__ == '__main__':
    # parse options
    opts, filenames = getopt.getopt(sys.argv[1:], 'hwmp:')
    should_test_moses = False
    should_test_worker = False
    help = False
    port = 0
    for opt, arg in opts:
        if opt == '-w':
            should_test_worker = True
        elif opt == '-h':
            help = True
        elif opt == '-m':
            should_test_moses = True
        elif opt == '-p':
            port = int(arg)
    # display help
    if filenames or (not should_test_moses ^ should_test_worker) or \
            not port or help:
        display_usage()
        sys.exit(1)
    test_ok = True
    # run tests
    if should_test_moses:
        test_ok &= test_moses(port)
    elif should_test_worker:
        test_ok &= test_worker(port)
    sys.exit(0 if test_ok else 1)

#!/usr/bin/env python

import SimpleXMLRPCServer
import SocketServer
import logging
import os
import sys
import getopt
import ast
import requests
from configobj import ConfigObj
from tasks.marian_translate import MarianTranslator
import socket
import atexit
import signal

class ThreadedXMLRPCServer(SocketServer.ThreadingMixIn,
                           SimpleXMLRPCServer.SimpleXMLRPCServer):
    """Multithreaded SimpleXMLRPCServer"""
    pass

class MTMonkeyMarianWorker(object):
    """Processes tasks ('translate' is currently the only implemented one)"""

    def __init__(self, config, logger):
        """Create the translator object that will handle translation"""
        # Marian translator (just passes data to a Marian server)
        self._translator = MarianTranslator(config.get('TRANSLATE_HOST'),
                                            config.get('TRANSLATE_PORT'),
                                            config.get('TRANSLATE_PATH'),
                                            config.get('SOURCE_LANG', 'en'),
                                            config.get('TARGET_LANG', 'en'),
                                            config.get('PREPROCESS', ''),
                                            config.get('POSTPROCESS', ''))
        self._logger = logger

    def process_task(self, task):
        """Process one task. Only 'translate' action is currently implemented."""
        if task['action'] == 'translate':
            self._logger.info("New translate task")
            try:
                try:
                    return self._translator.process_task(task)
                # check for translation server overload, crash nicely
                except socket.error as se:
                    if se.strerror in ['Connection reset by peer', 'Connection timed out']:
                        self._logger.warning('Translation server overloaded: ' + str(se))
                        return {'error' : 'Translation server overloaded.',
                                'errorCode': 2}
                    raise se
            # crash badly if any other error occurs
            except Exception as e:
                import traceback
                etype, eobj, etb = sys.exc_info()
                fname = os.path.split(etb.tb_frame.f_code.co_filename)[1]
                self._logger.warning('Translation error ' + traceback.format_exc())
                return {'error' : str(etype) + ' at ' + fname + ':' +
                        str(etb.tb_lineno) + "\n" + traceback.format_exc()}
        else:
            self._logger.warning('Unknown task ' + task['action'])
            return {'error' : 'Unknown task ' + task['action']}

    def alive_check(self):
        """Just checking that the server is up and running."""
        return 1

class AppServerInterface(object):
    def __init__(self, server_url, passphrase):
        self._server_url = server_url
        self._passphrase = passphrase

    def register(self, src_lang, tgt_lang, port, addr):
        data = {
            "action": "register",
            "passPhrase": self._passphrase,
            "sourceLang": src_lang,
            "targetLang": tgt_lang,
            "port": int(port),
        }
        if addr:
            data['address'] = addr
        req = requests.post(self._server_url + "/worker-api", json=data)

        print req.json()

    def remove(self, src_lang, tgt_lang, port, addr):
        data = {
            "action": "remove",
            "passPhrase": self._passphrase,
            "sourceLang": src_lang,
            "targetLang": tgt_lang,
            "port": int(port),
        }
        if addr:
            data['address'] = addr
        req = requests.post(self._server_url + "/worker-api", json=data)

        print req.json()

def main():
    # set up logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(message)s")
    logger = logging.getLogger('worker')

    # load configuration
    config = ConfigObj("marian_worker.cfg")

    # read command-line options
    opts, args = getopt.getopt(sys.argv[1:], 'c:')
    for opt, arg in opts:
        if opt == '-c':
            config.merge(ConfigObj(arg))
            logger.info("Merged configuration file: " + arg)
        else:
            logger.error("Unknown command-line option: " + opt)

    logger.info("Configuration loaded")

    # Create server
    logger.info("Starting XML-RPC server on port " + config['PORT'])
    server = ThreadedXMLRPCServer(("", int(config['PORT'])))
    server.register_introspection_functions()
    server.register_instance(MTMonkeyMarianWorker(config, logger))

    logger.info("Server started")

    print config

    # Depending on configuration, also register the worker with the appserver.
    if 'APPSERVER_URL' in config:
        if not 'PASSPHRASE' in config:
            raise Exception("Appserver URL for registration given but no passphrase")
        
        port = config['PORT']
        if 'PUBLIC_PORT' in config:
            # We are a Docker container or some other weirdness, the port visible to
            # the outside world differs from our config['PORT']. This variable tells
            # us the real port so that we can correctly register with the appserver.
            port = config['PUBLIC_PORT']

        addr = None
        if 'PUBLIC_ADDR' in config:
            # Also report the IP address that we are visible on. This can be useful
            # e.g. when running inside a virtual machine.
            addr = config['PUBLIC_ADDR']

        appserver = AppServerInterface(config['APPSERVER_URL'], config['PASSPHRASE'])
        logger.info("registering with appserver: " + config['APPSERVER_URL'])
        try:
            # register the worker
            appserver.register(config['SOURCE_LANG'], config['TARGET_LANG'], port, addr)

            # also gracefully unregister ourselves at exit
            remove_fn = lambda: appserver.remove(config['SOURCE_LANG'], config['TARGET_LANG'], port, addr)
            exit_fn = lambda x, y: sys.exit(0)

            atexit.register(remove_fn)
            signal.signal(signal.SIGTERM, exit_fn)

        except Exception as e:
            logger.error("failed to register worker with appserver: " + str(e))

    # Run the server's main loop
    server.serve_forever()

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import SimpleXMLRPCServer
import SocketServer
import logging
import os
import sys
import getopt
import ast
from configobj import ConfigObj
from tasks.translate import MosesTranslator, StandaloneTranslator
import socket

class ThreadedXMLRPCServer(SocketServer.ThreadingMixIn,
                           SimpleXMLRPCServer.SimpleXMLRPCServer):
    """Multithreaded SimpleXMLRPCServer"""
    pass

class MTMonkeyWorker(object):
    """Processes tasks ('translate' is currently the only implemented one)"""

    def __init__(self, config, logger):
        """Create the translator object that will handle translation"""
        # Standalone translator (just passes data to a XMLRPC server that handles everything)
        if config.get('TRANSLATOR_TYPE', '').lower() == 'standalone':
            self._translator = StandaloneTranslator(config['TRANSLATE_PORT'], 
                                                    config.get('TRANSLATE_URL_PATH', ''),
                                                    config.get('SRC_KEY', 'text'),
                                                    config.get('TGT_KEY', 'translated'),
                                                    ast.literal_eval(config.get('TRANSL_SETTING', '{}')))
        # Moses translator (only the translation itself is done by Moses XMLRPC server)
        else:
            self._translator = MosesTranslator(config['TRANSLATE_PORT'],
                                               config['RECASE_PORT'],
                                               config.get('SOURCE_LANG', 'en'),
                                               config.get('TARGET_LANG', 'en'))
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

def main():
    # set up logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(message)s")
    logger = logging.getLogger('worker')

    # load configuration
    config = ConfigObj("worker.cfg")

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
    server.register_instance(MTMonkeyWorker(config, logger))

    logger.info("Server started")

    # Run the server's main loop
    server.serve_forever()

if __name__ == "__main__":
    main()

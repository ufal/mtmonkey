#!/usr/bin/env python

import SimpleXMLRPCServer
import SocketServer
import logging
import os
import sys
import getopt
from configobj import ConfigObj
from tasks.translate import Translator

class ThreadedXMLRPCServer(SocketServer.ThreadingMixIn,
                           SimpleXMLRPCServer.SimpleXMLRPCServer):
    """Multithreaded SimpleXMLRPCServer"""
    pass

class KhresmoiWorker:
    """Processes tasks"""

    def __init__(self, config, logger):
        self._translator = Translator(config['TRANSLATE_PORT'], config['RECASE_PORT'])
        self._logger = logger

    def process_task(self, task):
        """Process one task. Only 'translate' action is currently implemented."""
        if task['action'] == 'translate':
            self._logger.info("New translate task")
            try:
                return self._translator.process_task(task)
            except Exception as e:
                import traceback
                etype, eobj, etb = sys.exc_info()
                fname = os.path.split(etb.tb_frame.f_code.co_filename)[1]
                return { 'error' : str(etype) + ' at ' + fname + ':' + str(etb.tb_lineno) + "\n" + traceback.format_exc() }
        else:
            self._logger.warning("Unknown task " + task['action'])
            return { 'error' : 'Unknown task ' + task['action'] }
    
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
    server.register_instance(KhresmoiWorker(config, logger))

    logger.info("Server started")

    # Run the server's main loop
    server.serve_forever()

if __name__ == "__main__":
    main()

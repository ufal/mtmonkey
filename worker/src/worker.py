#!/usr/bin/env python

import SimpleXMLRPCServer
import SocketServer
import logging
import os
from configobj import ConfigObj
from tasks import translate

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger('worker')

class ThreadedXMLRPCServer(SocketServer.ThreadingMixIn,
                           SimpleXMLRPCServer.SimpleXMLRPCServer):
    """Multithreaded SimpleXMLRPCServer"""
    pass

def process_task(task):
    """Process one task. Only 'translate' action is currently implemented."""
    if task['action'] == 'translate':
        logger.info("New translate task")
        return translate.process_task(task)
    else:
        logger.warning("Unknown task " + task['action'])
        return { 'error' : 'Unknown task ' + task['action'] }

def main():
    # load configuration
    config = ConfigObj("worker.cfg")

    # Overwrite default settings by envvar
    try:
        logger.info("Merging configuration file: " + os.environ['MICROTASK_SETTINGS'])
        config.merge(ConfigObj(os.environ['MICROTASK_SETTINGS']))
    except:
        pass

    logger.info("Loaded configuration file")

    # Create server
    logger.info("Starting XML-RPC server...")
    server = ThreadedXMLRPCServer((config['HOST'], int(config['PORT'])))
    server.register_introspection_functions()

    server.register_function(process_task)
    logger.info("Server started")

    # Run the server's main loop
    server.serve_forever()

if __name__ == "__main__":
    main()

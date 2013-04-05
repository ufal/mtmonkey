#!/usr/bin/env python

import SimpleXMLRPCServer
import SocketServer
from configobj import ConfigObj
from tasks import translate

class ThreadedXMLRPCServer(SocketServer.ThreadingMixIn,
                           SimpleXMLRPCServer.SimpleXMLRPCServer):
    """Multithreaded SimpleXMLRPCServer"""
    pass

def process_task(task):
    if task['action'] == 'translate':
        return translate.process_task(task)
    else:
        return { 'error' : 'Uknown task ' + task['action'] }

def main():
    # load configuration
    config = ConfigObj("worker.cfg")

    # Create server
    server = ThreadedXMLRPCServer((config['HOST'], int(config['PORT'])))
    server.register_introspection_functions()
    
    server.register_function(process_task)
    
    # Run the server's main loop
    server.serve_forever()

if __name__ == "__main__":
    main()

#!/usr/bin/env python

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from configobj import ConfigObj

def process_task(task):
  return {
    'translation': [
    {
      "translationId": 12345,
      "translated": [ { 'text': "test", 'score': 100, 'rank': 0 } ],
    }
    ]
  }

def main():
    # load configuration
    config = ConfigObj("worker.cfg")

    # Create server
    server = SimpleXMLRPCServer(("localhost", int(config['PORT'])))
    server.register_introspection_functions()
    
    server.register_function(process_task)
    
    # Run the server's main loop
    server.serve_forever()

if __name__ == "__main__":
    main()

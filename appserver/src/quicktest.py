#!/usr/bin/env python

import sys
import urllib2
# import httplib
import json

# SERVER = "195.113.20.53"
SERVER = "localhost"
PORT   = "8883"

def logmsg(msg):
    sys.stderr.write(str(msg) + "\n")

logmsg("Trying GET")
req = urllib2.Request("http://" + SERVER + ":" + PORT + "/khresmoi?sourceLang=en&targetLang=de&text=testing")
logmsg(urllib2.urlopen(req).read())

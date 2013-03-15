#!/usr/bin/env python

import sys
import urllib2
# import httplib
import json

SERVER = "192.168.0.11"
PORT   = "8883"

def logmsg(msg):
    sys.stderr.write(str(msg) + "\n")

logmsg("Trying GET")
req = urllib2.Request("http://" + SERVER + ":" + PORT + "/khresmoi?sourceLang=en&targetLang=cs&text=testing")
logmsg(urllib2.urlopen(req).read())

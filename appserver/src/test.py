import xmlrpclib

p = xmlrpclib.ServerProxy("http://192.168.0.11:9000/RPC2")
a = p.translate({ 'text': 'nein , das hund ist gut .' })
print a

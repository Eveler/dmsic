# -*- coding: utf-8 -*-

from ladon.server.wsgi import LadonWSGIApplication
import wsgiref.simple_server
from threading import Thread
import os

service_modules = [
	'stringtests',
	'typetests',
	'attachmenttests',
	'jsonrpc10',
	'collectiontest'
]

def make_server():
	global service_modules
	application = LadonWSGIApplication(service_modules,[os.path.join(os.path.dirname(__file__),'services')])
	server = wsgiref.simple_server.make_server('', 2376, application)
	return server

class ServiceThread(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.server = make_server()

	def run(self):
		self.server.serve_forever()

def serve_test_service(as_thread=False):
	if as_thread:
		t = ServiceThread()
		t.start()
		return t
	else:
		server = make_server()
		server.serve_forever()
	return None
    
if __name__=='__main__':
	serve_test_service()

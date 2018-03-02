# -*- coding: utf-8 -*-

import unittest
import servicerunner
import sys
import xml.dom.minidom as md
if sys.version_info[0]>=3:
	from urllib.parse import urlparse,splitport
	from http.client import HTTPConnection, HTTPSConnection
else:
	from urllib import splitport
	from urlparse import urlparse
	from httplib import HTTPConnection, HTTPSConnection
import sys,json
from ladon.compat import PORTABLE_BYTES,PORTABLE_STRING,PORTABLE_STRING_TYPES
from testladon import HTTPRequestPoster
from testladon import str_to_portable_string
import binascii

class JsonRpc10Tests(unittest.TestCase):

	def setUp(self):
		self.post_helper = HTTPRequestPoster('http://localhost:2376/JsonPrc10Service')

	def test_get_string(self):
		req = {'method':'return_string','params':None,'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')

		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		expected_result = str_to_portable_string('Yo!!!')
		self.assertEqual(res['result'], expected_result)
		
	def test_get_int(self):
		req = {'method':'return_int','params':None,'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		expected_result = 11
		self.assertEqual(res['result'], expected_result)
	
	def test_get_float(self):
		req = {'method':'return_float','params':None,'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		expected_result = 11.11
		self.assertEqual(res['result'], expected_result)
		
	def test_get_bool(self):
		req = {'method':'return_bool','params':None,'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		expected_result = True
		self.assertEqual(res['result'], expected_result)
		
	def test_get_bytes(self):
		req = {'method':'return_bytes','params':None,'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		expected_result = 'Yo!!!'
		self.assertEqual(res['result'], expected_result)
		
	def test_passback_string(self):
		val = 'Yo!!!'
		req = {'method':'passback_string','params':[val],'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')

		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		expected_result = str_to_portable_string(val)
		self.assertEqual(res['result'], expected_result)
		
	def test_passback_int(self):
		val = 11
		req = {'method':'passback_int','params':[val],'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		expected_result = val
		self.assertEqual(res['result'], expected_result)
	
	def test_passback_float(self):
		val = 11.11
		req = {'method':'passback_float','params':[val],'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		expected_result = val
		self.assertEqual(res['result'], expected_result)
		
	def test_passback_bool(self):
		val = True
		req = {'method':'passback_bool','params':[val],'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		expected_result = val
		self.assertEqual(res['result'], expected_result)
		
	def test_passback_bytes(self):
		val = 'Yo!!!'
		req = {'method':'passback_bytes','params':[val],'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		self.assertEqual(res['result'], val)
		
	def test_validate_request_response_structure(self):
		req = {}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))

		self.assertIs(type(res['error']), dict)
		self.assertTrue('id' is not res)
		self.assertIs(res['result'], None)
		self.assertTrue('"method"' in res['error']['string'])
		
		req = {'method':'passback_string'}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		self.assertIs(type(res['error']), dict)
		self.assertTrue('id' is not res)
		self.assertIs(res['result'], None)
		self.assertTrue('"params"' in res['error']['string'])
		
		req = {'method':'passback_string','params':None}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		self.assertIs(type(res['error']), dict)
		self.assertTrue('id' is not res)
		self.assertIs(res['result'], None)
		self.assertTrue('"id"' in res['error']['string'])
		
		req = {'method':'passback_string','params':None,'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		
		self.assertIs(type(res['error']), dict)
		self.assertEqual(res['id'], '0')
		self.assertIs(res['result'], None)
		
		req = {'method':'passback_string','params':None,'id':'0'}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		
		self.assertIs(type(res['error']), dict)
		self.assertEqual(res['id'], '0')
		self.assertIs(res['result'], None)
		
		req = {'method':'passback_string','params':['Yo!!!'],'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))

		self.assertIs(res['error'], None)
		self.assertEqual(res['id'], '0')
		self.assertEqual(res['result'], 'Yo!!!')
		
		req = {'method':'params','params':[],'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))

		self.assertIs(type(res['error']), dict)
		self.assertEqual(res['id'], '0')
		self.assertTrue('"arg0"' in res['error']['string'])
		
		req = {'method':'params','params':[11],'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))

		self.assertIs(type(res['error']), dict)
		self.assertEqual(res['id'], '0')
		self.assertTrue('"arg1"' in res['error']['string'])
		
		req = {'method':'params','params':[11, 11.11],'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))

		self.assertIs(type(res['error']), dict)
		self.assertEqual(res['id'], '0')
		self.assertTrue('"arg2"' in res['error']['string'])
		
		req = {'method':'params','params':[11,11.11,'Yo!!!','Yo!!!'],'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))

		self.assertIs(type(res['error']), dict)
		self.assertEqual(res['id'], '0')
		self.assertTrue('3' in res['error']['string'])
		self.assertTrue('4' in res['error']['string'])
		
		req = {'method':'params','params':{},'id':0}
		jreq = json.dumps(req)
		
		status,reason,resdata = self.post_helper.post_request(jreq.encode('utf-8'),extra_path='jsonrpc10',encoding='utf-8')
		
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))

		self.assertIs(type(res['error']), dict)
		self.assertEqual(res['id'], '0')
		self.assertTrue('Params must be array of objects.' == res['error']['string'])

if __name__ == '__main__':
	import servicerunner
	servicerunner
	service_thread = servicerunner.serve_test_service(as_thread=True)
	unittest.main(exit=False)
	service_thread.server.shutdown()
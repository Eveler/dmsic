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

def str_to_portable_string(in_str):
	"""
	Assumes that we always use UTF-8 encoding in script files
	"""
	if sys.version_info[0]>=3:
		return in_str
	else:
		return PORTABLE_STRING(in_str,'utf-8')


class HTTPRequestPoster(object):
	
	def __init__(self,url):
		self.valid_url = True
		parseres = urlparse(url)
		self.scheme = parseres.scheme
		if self.scheme.lower()=="https":
			self.port = 443
		elif self.scheme.lower()=="http":
			self.port = 80
		else:
			self.valid_url = False
		self.hostname,custom_port = splitport(parseres.netloc)
		if str(custom_port).isdigit():
			self.port = int(custom_port)
		self.path = parseres.path
	
	def post_request(self,data,extra_path="jsonwsp",encoding="utf-8"):
		headers = {
			"Content-type": "application/json, charset=%s" % encoding,
			"Accept": "application/json" }
		if self.scheme.lower()=='https':
			conn = HTTPSConnection(self.hostname,self.port)
		else:
			conn = HTTPConnection(self.hostname,self.port)
		req_path = self.path + '/' + extra_path
		conn.request("POST", req_path, data, headers)
		response = conn.getresponse()
		status, reason = response.status, response.reason
		resdata = response.read()
		conn.close()
		return status,reason,resdata


class StringTests(unittest.TestCase):

	def setUp(self):
		self.post_helper = HTTPRequestPoster('http://localhost:2376/StringTestService')

	def string_integrety_tests_json(self,methodname):
		fp_req = open('data/stringtests/in_out_test.json','rb')
		req = PORTABLE_STRING(fp_req.read(),'utf-8')
		fp_req.close()
		req = json.loads(req)
		req['methodname'] = methodname
		req = json.dumps(req)
		
		# utf-8 encoded request to bytesEncodingTest
		status,reason,resdata = self.post_helper.post_request(req.encode('utf-8'),encoding='utf-8')
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'utf-8'))
		expected_result = str_to_portable_string('äöüÄÖÄæøåÆØÅß')
		self.assertEqual(res['result'], expected_result)
		
		# latin-1 encoded request to bytesEncodingTest
		status,reason,resdata = self.post_helper.post_request(req.encode('latin-1'),encoding='latin-1')
		self.assertEqual(status, 200)
		res = json.loads(PORTABLE_STRING(resdata,'latin-1'))
		self.assertEqual(res['result'], expected_result)


	def string_integrety_tests_soap(self,methodname):
		fp_req = open('data/stringtests/in_out_test.soap','rb')
		req = fp_req.read()
		fp_req.close()
		req = md.parseString(req)
		req.getElementsByTagNameNS('*','in_out_method')[0].tagName = str_to_portable_string('mns:%s' % methodname)

		expected_result = str_to_portable_string('äöüÄÖÄæøåÆØÅß')

		# utf-8 encoded request to bytesEncodingTest
		status,reason,resdata = self.post_helper.post_request(req.toxml(encoding='utf-8'),extra_path='soap',encoding='utf-8')
		self.assertEqual(status, 200)
		res = md.parseString(resdata)
		result_string = res.getElementsByTagName('result')[0].childNodes[0].data
		self.assertEqual(result_string, expected_result)
		
		# latin-1 encoded request to bytesEncodingTest
		status,reason,resdata = self.post_helper.post_request(req.toxml(encoding='latin-1'),extra_path='soap',encoding='latin-1')
		self.assertEqual(status, 200)
		res = md.parseString(resdata)
		result_string = res.getElementsByTagName('result')[0].childNodes[0].data
		self.assertEqual(result_string, expected_result)

	def test_bytes_in_bytes_out_json(self):
		self.string_integrety_tests_json('bytes_in_bytes_out')
		
	def test_bytes_in_uni_out_json(self):
		self.string_integrety_tests_json('bytes_in_uni_out')
		
	def test_uni_in_bytes_out_json(self):
		self.string_integrety_tests_json('uni_in_bytes_out')
		
	def test_uni_in_uni_out_json(self):
		self.string_integrety_tests_json('uni_in_uni_out')

	def test_bytes_in_bytes_out_soap(self):
		self.string_integrety_tests_soap('bytes_in_bytes_out')
		
	def test_bytes_in_uni_out_soap(self):
		self.string_integrety_tests_soap('bytes_in_uni_out')
		
	def test_uni_in_bytes_out_soap(self):
		self.string_integrety_tests_soap('uni_in_bytes_out')
		
	def test_uni_in_uni_out_soap(self):
		self.string_integrety_tests_soap('uni_in_uni_out')



if __name__ == '__main__':
	import servicerunner
	servicerunner
	service_thread = servicerunner.serve_test_service(as_thread=True)
	unittest.main(exit=False)
	service_thread.server.shutdown()


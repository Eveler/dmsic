import sys, os
# uncomment line below if you need to run the tests separately from installed ladon library
#sys.path.insert(0, os.path.realpath("%s/../src" %os.getcwd()))
sys.path.insert(0, "%s/services" %os.getcwd())
from collectiontest import *

import unittest
import servicerunner
import xml.dom.minidom as md
if sys.version_info[0]>=3:
	from urllib.parse import urlparse,splitport
	from http.client import HTTPConnection, HTTPSConnection
else:
	from urllib import splitport
	from urlparse import urlparse
	from httplib import HTTPConnection, HTTPSConnection
import json
from ladon.compat import PORTABLE_BYTES,PORTABLE_STRING,PORTABLE_STRING_TYPES
from ladon.ladonizer.collection import *

class TestGlobalServiceCollection(unittest.TestCase):
	def setUp(self):
		self.test_service = CollectionTestService
		self.collection   = global_service_collection()
		self.service      = self.collection \
			.services_by_name(self.test_service.__name__)[0]

		unittest.TestCase.setUp(self)

	def test01_get_real_method(self):
		print( "Testing LadonMethodInfo::get_real_method()")
		search_method_name = 'method_one'
		method_name = self.test_service.method_one._ladon_method_info.get_real_method().__name__
		self.assertEqual(method_name, search_method_name)

	def test02_services_by_function(self):
		print( "Testing LadonServiceCollection::services_by_function()")
		fn = self.test_service.method_one._ladon_method_info.get_real_method()
		service_name = self.collection.services_by_function(fn)[0].servicename
		self.assertEqual(service_name, self.test_service.__name__)

	def test03_remove_service_append_service(self):
		# test remove
		print( "Testing LadonServiceCollection::remove_service()")
		self.collection.remove_service(self.service.sourcefile, self.service.servicename)
		self.assertEqual(
			self.collection.services_by_name(self.service.servicename),
			[])

		# test append
		print( "Testing LadonServiceCollection::append_service()")
		self.collection.append_service(self.service) # revert removal
		self.assertEqual(
			self.collection.services_by_name(self.service.servicename),
			[self.service])

	def test04_services_remove_by_name(self):
		print( "Testing LadonServiceCollection::services_remove_by_name()")
		self.collection.services_remove_by_name(self.service.servicename)
		
		self.assertEqual(self.collection.services_by_name(self.service.servicename), [])
		self.collection.append_service(self.service) # revert removal

	def test05_has_service(self):
		print( "Testing LadonServiceCollection::has_service()")
		self.assertEqual(
			self.collection.has_service(
				self.service.sourcefile,
				self.service.servicename),
			True)

		self.assertEqual(
			self.collection.has_service(
				self.service.sourcefile,
				"Fake%s" %self.service.servicename),
			False)
	
	def test06_has_method(self):
		print( "Testing LadonServiceInfo::has_method()")
		self.assertEqual(self.service.has_method('method_one'), True)
		self.assertEqual(self.service.has_method('fake_method_one'), False)

	def test07_remove_method_append_method(self):
		methods     = self.service.method_list()
		method      = methods[0]
		method_name = method.name()
		methods_len = len(methods)

		# test remove method
		print( "Testing LadonServiceInfo::remove_method()")
		rmethod = self.service.remove_method(method_name)
		self.assertEqual(rmethod == method, True)
		self.assertEqual(len(self.service.method_list()), methods_len - 1)
		self.assertEqual(rmethod in self.service.method_list(), False)

		# test append method
		print( "Testing LadonServiceInfo::append_method()")
		self.service.append_method(rmethod)
		self.assertEqual(len(self.service.method_list()), methods_len)
		self.assertEqual(rmethod in self.service.method_list(), True)

	def test08_add_arg_remove_arg(self):
		print( "Testing LadonMethodInfo::add_arg()")
		method = self.service.method('method_one')
		
		method.add_arg('arg1', PORTABLE_STRING, 'Test argument 1')
		method.add_arg('arg2', PORTABLE_STRING, ['Test argument 2'], True)

		self.assertEqual(len(method.args()), 2)

		print( "Testing LadonMethodInfo::remove_arg()")
		method.remove_arg('arg1')
		method.remove_arg('arg2')

		self.assertEqual(len(method.args()), 0)

	def test09_arg_insert_before(self):
		print( "Testing LadonMethodInfo::arg_insert_before()")
		method = self.service.method('method_one')
		
		method.add_arg('arg1', PORTABLE_STRING, 'Test argument 1')
		method.add_arg('arg2', PORTABLE_STRING, ['Test argument 2'], True)

		method.arg_insert_before('arg2', 'arg3', PORTABLE_STRING, 'Test argument 3')

		self.assertEqual(len(method.args()), 3)
		self.assertEqual(method.args()[1]['name'], 'arg3')

		# revert
		for arg in ['arg1', 'arg2', 'arg3']:
			method.remove_arg( arg)

	def test10_arg_insert_after(self):
		print( "Testing LadonMethodInfo::arg_insert_after()")
		method = self.service.method('method_one')
		
		method.add_arg('arg1', PORTABLE_STRING, 'Test argument 1')
		method.add_arg('arg2', PORTABLE_STRING, ['Test argument 2'], True)

		method.arg_insert_after('arg1', 'arg3', PORTABLE_STRING, 'Test argument 3')

		self.assertEqual(len(method.args()), 3)
		self.assertEqual(method.args()[1]['name'], 'arg3')

		# revert
		for arg in ['arg1', 'arg2', 'arg3']:
			method.remove_arg(arg)

	def test11_has_arg(self):
		print( "Testing LadonMethodInfo::has_arg()")
		method = self.service.method('method_one')
		method.add_arg('arg1', PORTABLE_STRING, 'Test argument 1')

		self.assertEqual(method.has_arg('arg1'), True)
		self.assertEqual(method.has_arg('arg2'), False)
		
		method.remove_arg('arg1') # revert

if __name__ == '__main__':
	import servicerunner
	servicerunner
	service_thread = servicerunner.serve_test_service(as_thread=True)
	unittest.main(exit=False)
	service_thread.server.shutdown()

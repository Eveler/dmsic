# -*- coding: utf-8 -*-

import inspect

class BaseInterface(object):
	"""All interface implementations must descend from BaseInterface. The interface
	implementation can be thought of as an aggregator that ties the three basic functions
	of a web service protocol together:
	
		1. ServiceDescriptor - A generator class that can provide a description for the service.
		   ie. WSDL for soap.
		2. BaseRequestHandler - A handler that can parse the raw request objects from the client and
		   convert them into a so-called req_dict (Request dictionary)
		3. BaseResponseHandler - A handler that can process the res_dict (Result Dictionary) of a
		   service call and build a response object that fit's the protocol being implemented.
		4. BaseFaultHandler - A handler that can convert a ladon.exceptions.service.ServiceFault object
		   to a fault response that fits the interface.
	
	"""
	def __init__(self,sinfo,**kw):
		self._sinfo = sinfo
		sd = ServiceDescriptor()
		if 'service_descriptor' in kw:
			sd = kw['service_descriptor']
			if inspect.getmro(sd).count(ServiceDescriptor):
				self._service_descriptor = sd()
		if 'request_handler' in kw:
			req_handler = kw['request_handler']
			if inspect.getmro(req_handler).count(BaseRequestHandler):
				self._request_handler = req_handler()
		if 'response_handler' in kw:
			resp_handler = kw['response_handler']
			if inspect.getmro(resp_handler).count(BaseResponseHandler):
				self._response_handler = resp_handler()
		if 'fault_handler' in kw:
			fault_handler = kw['fault_handler']
			if inspect.getmro(fault_handler).count(BaseFaultHandler):
				self._fault_handler = fault_handler()

	@staticmethod
	def _interface_name(typ):
		return None

	@staticmethod
	def _accept_basetype(typ):
		return False

	@staticmethod
	def _accept_list():
		return False

	@staticmethod
	def _accept_dict():
		return False
	
	def service_info(self):
		return self._sinfo
	
	def parse_request(self,soap_body,encoding='UTF-8'):
		return self._request_handler.parse_request(soap_body,self._sinfo,encoding)

	def build_response(self,res_dict,encoding='UTF-8'):
		return self._response_handler.build_response(res_dict,self._sinfo,encoding)

	def build_fault_response(self,exc,methodname=None,encoding='UTF-8',reflection=None):
		return self._fault_handler.build_fault_response(exc,self._sinfo,methodname,encoding,reflection)

	def stringify_res_dict(self):
		return self._response_handler._stringify_res_dict

	def response_content_type(self):
		return self._response_handler._content_type

	def description(self,service_url,encoding='UTF-8',**kw):
		return self._service_descriptor.generate(
			self._sinfo.servicename,
			self._sinfo.servicenumber,
			self._sinfo.typemanager,
			self._sinfo.method_list(),
			service_url,encoding,
			**kw)

	def description_content_type(self):
		return self._service_descriptor._content_type

class ServiceDescriptor(object):
	
	_content_type = 'text/plain'
	
	def generate(self,servicename,servicenumber,typemanager,methodlist,encoding,**kw):
		"""
		Implement the method that can generate a service description file for the
		type of interface you are developing. Thus if you were developing a new
		and better SOAP interface and a new and better service descriptor for it,
		you will be implementing a WSDL generator in this method.
		
		@param servicename This is a string containing the service class name
		@param servicenumber An integer that reflects the order in which the service classes are parsed (useful for creating namespaces)
		@param typemanager An instance of ladon.ladonizer.collection.TypeManager which manages the types used by the service
		@param methodlist The list of methods exposed by the service
		@param encoding The client-side controlled encoding to use in the descriptor
		
		@rtype String representation of the service descriptor (ie. wsdl-formatted if it were SOAP)
		"""
		return ''


class BaseRequestHandler(object):
	
	def parse_request(self,req,sinfo,encoding):
		return {}


class BaseResponseHandler(object):
	
	"""
	This is the base class of all response handlers. To implement a new response handler
	inherit it and overload the build_response() method so it implements the protocol you are
	extending Ladon with.
	
	set _stringify_res_dict to True if you want the Ladon dispatcher to convert all result
	values to unicode regardless of their defined types during ladonization. This can be useful
	in some interfaces. ie. SOAP where all values are presented the same way inside XML tags no
	matter if it is a string or a number (example: <name>string</name><age>37</age>)
	"""
	_content_type = 'text/plain'
	_stringify_res_dict = False
	
	def build_response(self,method_result,sinfo,encoding):
		return ''

class BaseFaultHandler(object):
	
	"""
	This is the base class of all fault handlers. To implement a new fault handler
	inherit it and overload the build_fault_response() method so it implements the
	protocol you are extending Ladon with.
	
	set _stringify_res_dict to True if you want the Ladon dispatcher to convert all result
	values to unicode regardless of their defined types during ladonization. This can be useful
	in some interfaces. ie. SOAP where all values are presented the same way inside XML tags no
	matter if it is a string or a number (example: <name>string</name><age>37</age>)
	"""
	_content_type = 'text/plain'
	_stringify_res_dict = False
	
	def build_fault_response(self,exc,sinfo,methodname,encoding):
		return ''

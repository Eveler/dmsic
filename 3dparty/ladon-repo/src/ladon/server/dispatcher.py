# -*- coding: utf-8 -*-

from ladon.ladonizer.collection import global_service_collection
from ladon.types import get_type_info,validate_type
from ladon.types.attachment import attachment,extract_attachment_reference
from ladon.types.typeconverter import TypeConverter
from ladon.exceptions.dispatcher import *
from ladon.exceptions.service import *
from ladon.tools.multiparthandler import AttachmentHandler
from ladon.server.customresponse import CustomResponse
from ladon.tools.log import info,debug
import os,re,traceback,time,json
from ladon.server import *

def get_client_address(environ):
	try:
		return environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
	except KeyError:
		return environ['REMOTE_ADDR']
	return ''

class Dispatcher(object):
	"""
	The dispatcher class handles the communication between the service interface and
	the user functionality. This happens in dispatch_request()
	
	1. It recieves the raw protocol data and attempts to parse it using the service
	interface's request handler. If successful a req_dict (request dictionary) is returned.

	2. The request dictionary is parsed to call_method() where the arguments are converted to
	fit the user defined method.
	
	3. If the call to the user defined method is successful the result is converted to a
	res_dict (response dictionary) in result_to_dict()
	
	4. The response dictionary is passed to the service interface's response handler and
	returned as raw protocol data.
	
	"""
	def __init__(self,sinst,ifclass,response_encoding,languages,logging):
		self.response_encoding = response_encoding
		self.languages = languages
		self.sinst = sinst
		self.iface = ifclass(sinst)
		self.logging = logging
		self.fault_hint = u''


	def call_method(self,method,req_dict,tc,export_dict,log_line):
		"""
		call_method converts the res_dict delivered from an interface
		to the type of arguments expected by the service method.
		tc is the TypeConverter associated to the service method.
		"""
		global rx_cid,rx_cidx
		args = []
		for arg in method.args():
			self.fault_hint = u'Processing incoming argument: "%s"' % arg['name']
			if arg['name'] not in req_dict['args']:
				if 'default' in arg:
					args += [arg['default']]
				else:
					raise UndefinedServiceMethod(self.iface._interface_name(),self.sinst.servicename,'Parameter "%s" is not optional' % arg['name'])
			else:
				if type(arg['type'])==list:
					arg_list = []
					type_info = get_type_info(arg['type'][0])
					if type_info:
						for item in req_dict['args'][arg['name']]:
							arg_list += [arg['type'][0](prime_dict=item,tc=tc,export_dict=export_dict)]
					elif arg['type'][0]==attachment:
						for item in req_dict['args'][arg['name']]:
							arg_list += [extract_attachment_reference(item,export_dict,self.response_encoding,self.iface._interface_name(),self.sinst.servicename)]
					else:
						for item in req_dict['args'][arg['name']]:
							arg_list += [tc.from_unicode_string(item,arg['type'][0])]
					args += [arg_list]
				else:
					type_info = get_type_info(arg['type'])
					val = req_dict['args'][arg['name']]
					if type_info:
						args += [arg['type'](prime_dict=val,tc=tc,export_dict=export_dict)]
					elif arg['type']==attachment:
						args += [extract_attachment_reference(val,export_dict,self.response_encoding,self.iface._interface_name(),self.sinst.servicename)]
					else:
						args += [tc.from_unicode_string(val,arg['type'])]
					
		#path,fname = os.path.split(method.sinfo.sourcefile)
		#mname = os.path.splitext(fname)[0]
		mname = method.sinfo.modulename
		service_module = __import__(mname, globals(),  locals(), '*')
		#file, pathname, description = imp.find_module(mname,[path])
		#service_module = imp.load_module(mname,file, pathname, description)
		service_class_instance = getattr(service_module,method.sinfo.servicename)()
		if self.logging & LOG_REQUEST_ACCESS:
			log_line['Method'] = '%s.%s' % (method.sinfo.servicename,req_dict['methodname'])
		if self.logging & LOG_REQUEST_DICT:
			log_line['RequestDict'] = req_dict
		if self.logging & LOG_EXECUTION_TIME:
			start = time.time()
		if method._has_keywords:
			kw = {'LADON_METHOD_TC':tc, 'LADON_METHOD_NAME':req_dict['methodname'], 'LADON_ACCEPT_LANGUAGES': self.languages}
			kw.update(export_dict)
			result = getattr(service_class_instance,req_dict['methodname'])(*args,**kw)
		else:
			result = getattr(service_class_instance,req_dict['methodname'])(*args)
		if self.logging & LOG_EXECUTION_TIME:
			log_line['ExecutionTime'] = time.time()-start
		return result

	def result_to_dict(self,method,result,tc,response_attachments,log_line):
		"""
		Convert the result of a method call to it's dictionary representation.
		tc is a TypeConverter
		"""
		res_dict = {
			'servicename': method.sinfo.servicename,
			'servicenumber': method.sinfo.servicenumber,
			'method': method.name()}
		typ = method._rtype
		type_info = get_type_info(typ)
		if type_info==None:
			if [list,tuple].count(type(typ)):
				result_list = []
				res_dict['result'] = result_list
				type_info = get_type_info(typ[0])
				if result == typ:
					# Assumption list attributes are always optional
					return
				
				if type_info:
					for item in result:
						result_list += [item.__dict__(tc,response_attachments)]
				elif typ[0]==attachment:
					for item in result:
						if not type(item) == attachment:
							raise AttachmentExpected(self.iface._interface_name(),self.sinst.servicename,'Attachment expected got: %s' % type(item))
						result_list += [response_attachments.add_attachment(item)]
				else:
					for item in result:
						result_list += [tc.to_unicode_string(item,typ[0])]
			elif typ==attachment:
				res_dict['result'] = response_attachments.add_attachment(result)
			else:
				res_dict['result'] = tc.to_unicode_string(result,typ)
		else:
			res_dict['result'] = result.__dict__(tc,response_attachments)
		
		if self.logging & LOG_RESPONSE_DICT:
			log_line['ResponseDict'] = res_dict
		return res_dict


	def dispatch_request(self,request_data,export_dict):
		log_line = {}
		try:
			export_dict['response_attachments'] = AttachmentHandler()
			methodname,method = None,None
			req_dict = self.iface.parse_request(request_data,encoding=self.response_encoding)
			methodname = req_dict['methodname']
			method = self.sinst.method(methodname)
			if not method:
				raise UndefinedServiceMethod(self.iface._interface_name(),self.sinst.servicename,'Service method "%s" is not declared in service' % methodname)
			tc = TypeConverter(
				encoding=method._encoding,
				allow_unsafe_conversion=method._allow_unsafe_conversion,
				only_strings_to_unicode=(not self.iface.stringify_res_dict()))
			result = self.call_method(method,req_dict,tc,export_dict,log_line)
		except Exception as e:
			reflection = req_dict.get('mirror',None)
			if isinstance(e,ServiceFault):
				response = self.iface.build_fault_response(e,methodname,encoding=self.response_encoding,reflection=reflection)
			elif method==None:
				response = self.iface.build_fault_response(ClientFault(str(e),hint=self.fault_hint),methodname,encoding=self.response_encoding,reflection=reflection)
			else:
				response = self.iface.build_fault_response(ServerFault(str(e),hint=self.fault_hint),methodname,encoding=self.response_encoding,reflection=reflection)
			return response
		if isinstance(result,CustomResponse):
			# In some cases it can be nessecary to override the normal response system and return
			# something completely different - ie. 
			# 1. if a certain method should return a file as a http attachment response for
			#    browsers (Content-Disposition: attachment;).
			# 2. or a commandline tool that sends a SOAP request and should output raw text as
			#    result
			# Objects of CustomResponse descendents are intercepted in the wsgi_application part
			# so the service developer has full control over response headers and data.
			return result
		res_dict = self.result_to_dict(method,result,tc,export_dict['response_attachments'],log_line=log_line)
		if 'mirror' in req_dict:
			res_dict['reflection'] = req_dict['mirror']
		if 'id' in req_dict:
			res_dict['id'] = req_dict['id']
		response = self.iface.build_response(res_dict,encoding=self.response_encoding)
		if self.logging:
			if self.logging & LOG_JSON_FORMAT:
				log_line['remote_addr'] = get_client_address(export_dict)
				info(json.dumps(log_line,ensure_ascii=False).encode(self.response_encoding))
			else:
				parts = []
				log_keys = ['Method', 'RequestDict', 'ExecutionTime', 'ResponseDict']
				for k in log_keys:
					if k in log_keys:
						parts += [ '%s:%s' % (k, str(log_line[k])) ]
				info('\t%s' % ('\t'.join(parts)))
		return response

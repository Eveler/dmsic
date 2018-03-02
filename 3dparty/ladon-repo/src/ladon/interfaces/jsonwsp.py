# -*- coding: utf-8 -*-

from ladon.interfaces.base import BaseInterface,ServiceDescriptor,BaseRequestHandler,BaseResponseHandler,BaseFaultHandler
from ladon.interfaces import expose
from ladon.compat import type_to_jsontype,pytype_support,PORTABLE_STRING
import json,sys,traceback

from threading import Lock
cache_lock = Lock()
jsonwsp_cache = {}

class JSONWSPServiceDescriptor(ServiceDescriptor):
	
	javascript_type_map = type_to_jsontype
	version = '1.1'
	_content_type = 'application/json'
	_ignored_dict_type_keys = ['filters']

	def generate(self,servicename,servicenumber,typemanager,methodlist,service_url,encoding,**kw):
		type_dict = typemanager.type_dict
		type_order = typemanager.type_order
		
		include_doc = kw.get('include_doc')!=None
		cache_key = "%d,%d,%s" % (servicenumber,include_doc,service_url)
		if cache_key in jsonwsp_cache:
			return jsonwsp_cache[cache_key]
		
		def map_type(typ):
			if typ in JSONWSPServiceDescriptor.javascript_type_map:
				return JSONWSPServiceDescriptor.javascript_type_map[typ]
			else:
				return typ.__name__

		desc = {
			'servicename': servicename,
			'url': service_url,
			'type': 'jsonwsp/description',
			'version': self.version,
			'types': {},
			'methods': {}
		}
		
		types = desc['types']
		for typ in type_order:
			if type(typ)==dict:
				desc_type = {}
				types[typ['name']] = desc_type
				for k,v,props in typ['attributes']:
					if type(v)==list:
						desc_type_val = [map_type(v[0])]
					else:
						desc_type_val = map_type(v)
					
					if self.version>'1.0':
						attr_props = dict(filter(lambda x: x[0] not in self._ignored_dict_type_keys + ([] if include_doc else ['doc']) , props.items()))
						attr_props['type'] = desc_type_val
						desc_type[k] = attr_props
					else:
						desc_type[k] = desc_type_val

		methods = desc['methods']
		for m in methodlist:
			desc_mparams = {}
			order = 1
			desc_method = {'params': desc_mparams, 'doc_lines': m._method_doc if include_doc else []}
			methods[m.name()] = desc_method
			for arg in m.args():
				if [list,tuple].count(type(arg['type'])):
					desc_param_type = [map_type(arg['type'][0])]
				else:
					desc_param_type = map_type(arg['type'])
				desc_mparams[arg['name']] = {
					"type": desc_param_type,
					"def_order": order,
					"optional": arg['optional'],
					}
				if include_doc and 'doc' in arg:
					desc_mparams[arg['name']]["doc_lines"] = arg['doc'] if include_doc else []
				else:
					desc_mparams[arg['name']]["doc_lines"] = []
				if 'default' in arg:
					desc_mparams[arg['name']]["default"] = PORTABLE_STRING(arg['default'])

				order += 1
				
			if [list,tuple].count(type(m._rtype)):
				desc_rtype = [map_type(m._rtype[0])]
			else:
				desc_rtype = map_type(m._rtype)
			desc_method['ret_info'] = {
				'type': desc_rtype,
				'doc_lines': m._rtype_doc if include_doc else []
			}
			
		if sys.version_info[0]>=3:
			return json.dumps(desc)
		json_desc = json.dumps(desc,encoding=encoding)
		cache_lock.acquire()
		jsonwsp_cache[cache_key] = json_desc
		cache_lock.release()
		return json_desc



class JSONWSPRequestHandler(BaseRequestHandler):
	
	def parse_request(self,json_body,sinfo,encoding):
		def parse_number(x):
			return PORTABLE_STRING(x)
		def parse_constant(x):
			#if x=='false':
				#return PORTABLE_STRING("False")
			#elif x=='true':
				#return PORTABLE_STRING("True")
			if x=='null':
				return PORTABLE_STRING("None")
			return PORTABLE_STRING(x)
		req_dict = json.loads(PORTABLE_STRING(json_body,encoding),parse_int=parse_number,parse_float=parse_number,parse_constant=parse_constant)
		return req_dict



class JSONWSPResponseHandler(BaseResponseHandler):
	
	_content_type = 'application/json'
	_stringify_res_dict = False
	version = '1.0'
	
	def build_response(self,res_dict,sinfo,encoding):
		res_dict['type'] = 'jsonwsp/response'
		res_dict['version'] = self.version
		res_dict['methodname'] = res_dict['method']
		del res_dict['method']
		return json.dumps(res_dict,ensure_ascii=False).encode(encoding)

class JSONWSPFaultHandler(BaseFaultHandler):
	
	_content_type = 'text/xml'
	_stringify_res_dict = False
	version = '1.0'
	
	def build_fault_response(self,service_exc,sinfo,methodname,encoding,reflection):
		if service_exc.detail:
			detail = service_exc.detail
		else:
			detail = traceback.format_exc()
		detail = detail.replace('\r\n','\n').split('\n')
		fault_dict = {
			'type': 'jsonwsp/fault',
			'version': self.version,
			'fault': {
				'code': service_exc.faultcode,
				'string': service_exc.faultstring,
				'detail': detail,
				'filename': service_exc.mod,
				'lineno': service_exc.lineno,
				'hint': service_exc.hint
			}
		}
		if reflection:
			fault_dict['reflection'] = reflection
		return json.dumps(fault_dict,ensure_ascii=False).encode(encoding)


@expose
class JSONWSPInterface(BaseInterface):

	def __init__(self,sinfo,**kw):
		def_kw = {
			'service_descriptor': JSONWSPServiceDescriptor,
			'request_handler': JSONWSPRequestHandler,
			'response_handler': JSONWSPResponseHandler,
			'fault_handler': JSONWSPFaultHandler}
		def_kw.update(kw)
		BaseInterface.__init__(self,sinfo,**def_kw)

	@staticmethod
	def _interface_name():
		return 'jsonwsp'

	@staticmethod
	def _accept_basetype(typ):
		return pytype_support.count(typ)>0

	@staticmethod
	def _accept_list():
		return True

	@staticmethod
	def _accept_dict():
		return False


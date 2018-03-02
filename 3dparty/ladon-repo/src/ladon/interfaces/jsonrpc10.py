# -*- coding: utf-8 -*-

from ladon.interfaces.base import BaseInterface,ServiceDescriptor,BaseRequestHandler,BaseResponseHandler,BaseFaultHandler
from ladon.interfaces import expose
from ladon.compat import type_to_jsontype,pytype_support,PORTABLE_STRING
import json,sys,traceback
from ladon.exceptions.service import ServiceFault
from ladon.exceptions.base import LadonException

def _add_passback_params(res_dict,passback_dict):
	merged_dict = dict((k,v) for (k,v) in res_dict.items())	
	for k,v in passback_dict.items():
		merged_dict[k] = v
	return merged_dict

class RequestPropFault(ServiceFault):
	def __init__(self,prop, passback_dict):
		self.prop = prop
		self.passback_dict = passback_dict
		super(RequestPropFault,self).__init__('service','Request doesn\'t have "%s" property.' % self.prop, None, 2)

	def __str__(self):
		return self.faultstring

class RequestParamFault(ServiceFault):
	def __init__(self,param, passback_dict):
		self.param = param
		self.passback_dict = passback_dict
		super(RequestParamFault,self).__init__('service','Request doesn\'t have "%s" parameter.' % self.param, None, 2)

	def __str__(self):
		return self.faultstring
	
class MethodArgsCountFault(ServiceFault):
	def __init__(self,methodname,targsscount,gargscount,passback_dict):
		self.methodname = methodname
		self.targsscount = targsscount
		self.gargscount = gargscount
		self.passback_dict = passback_dict
		super(MethodArgsCountFault,self).__init__('service','Method "%s" takes exactly %s arguments, %s given.' % \
			(self.methodname,self.targsscount,self.gargscount), None, 2)

	def __str__(self):
		return self.faultstring
	
class RequestParamsArrayFault(ServiceFault):
	def __init__(self,passback_dict):
		self.passback_dict = passback_dict
		super(RequestParamsArrayFault,self).__init__('service','Params must be array of objects.',None,2)

	def __str__(self):
		return self.faultstring

class JSONRPCServiceDescriptor(ServiceDescriptor):	
	javascript_type_map = type_to_jsontype
	version = '1.0'
	_content_type = 'application/json'

	def generate(self,servicename,servicenumber,typemanager,methodlist,service_url,encoding,**kw):
		type_dict = typemanager.type_dict
		type_order = typemanager.type_order

		def map_type(typ):
			if typ in JSONRPCServiceDescriptor.javascript_type_map:
				return JSONRPCServiceDescriptor.javascript_type_map[typ]
			else:
				return typ.__name__

		desc = {
			'servicename': servicename,
			'url': service_url,
			'type': 'jsonrpc/description',
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
					desc_type[k] = desc_type_val

		methods = desc['methods']
		for m in methodlist:
			desc_mparams = {}
			order = 1
			desc_method = {'params': desc_mparams, 'doc_lines': m._method_doc}
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
				if 'doc' in arg:
					desc_mparams[arg['name']]["doc_lines"] = arg['doc']
				else:
					desc_mparams[arg['name']]["doc_lines"] = []
				order += 1
				
			if [list,tuple].count(type(m._rtype)):
				desc_rtype = [map_type(m._rtype[0])]
			else:
				desc_rtype = map_type(m._rtype)
			desc_method['ret_info'] = {
				'type': desc_rtype,
				'doc_lines': m._rtype_doc
			}
			
		if sys.version_info[0]>=3:
			return json.dumps(desc)
		return json.dumps(desc,encoding=encoding)

class JSONRPCRequestHandler(BaseRequestHandler):
	def parse_request(self,json_body,sinfo,encoding):
		def parse_number(x):
			return PORTABLE_STRING(x)
		def parse_constant(x):
			if x=='null':
				return PORTABLE_STRING("None")
			return PORTABLE_STRING(x)
		req_dict = json.loads(PORTABLE_STRING(json_body,encoding), parse_int=parse_number, parse_float=parse_number, \
			parse_constant=parse_constant)
		passback_dict = self.get_passback_params(req_dict)
		if 'method' not in req_dict:
			raise RequestPropFault('method',passback_dict)
		if 'params' not in req_dict:
			raise RequestPropFault('params',passback_dict)
		if 'id' not in req_dict:
			raise RequestPropFault('id',passback_dict)
		minfo = sinfo.methods[req_dict['method']]
		params = req_dict['params']
		if params is not None and type(params) is not list:
			raise RequestParamsArrayFault(passback_dict)
		params_len = len(params) if params is not None else 0
		args_len = len(minfo.args())
		if params_len == 0 and  args_len> 0:
			raise RequestParamFault(minfo.args()[0]['name'],passback_dict)
		elif params_len < args_len:
			raise RequestParamFault(minfo.args()[params_len]['name'],passback_dict)
		elif params_len > args_len:
			raise MethodArgsCountFault(req_dict['method'], args_len, params_len,passback_dict)
		req_dict['args'] = {}
		if params is not None:
			for i in range(len(params)):
				req_dict['args'][minfo.args()[i]['name']] = params[i]
		req_dict['methodname'] = req_dict['method']
		del req_dict['params']
		del req_dict['method']
		return req_dict
	
	def get_passback_params(self, req_dict):
		if 'id' in req_dict:
			return {'id': req_dict['id']}
		else:
			return {}

class JSONRPCResponseHandler(BaseResponseHandler):
	_content_type = 'application/json'
	_stringify_res_dict = False
	
	def build_response(self,res_dict,sinfo,encoding):
		res_dict['error'] = None
		del res_dict['servicenumber']
		del res_dict['servicename']
		del res_dict['method']
		return json.dumps(res_dict,ensure_ascii=False).encode(encoding)

class JSONRPCFaultHandler(BaseFaultHandler):
	_content_type = 'application/json'
	_stringify_res_dict = False
	
	def build_fault_response(self,service_exc,sinfo,methodname,encoding,reflection):
		if service_exc.detail:
			detail = service_exc.detail
		else:
			detail = traceback.format_exc()
		detail = detail.replace('\r\n','\n').split('\n')
		fault_dict = {
			'result': None,
			'error': {
				'code': service_exc.faultcode,
				'string': service_exc.faultstring,
				'detail': detail,
				'filename': service_exc.mod,
				'lineno': service_exc.lineno,
				'hint': service_exc.hint
			},
		}
		if hasattr(service_exc,'passback_dict'):
			fault_dict = _add_passback_params(fault_dict,service_exc.passback_dict)
		return json.dumps(fault_dict,ensure_ascii=False).encode(encoding)

@expose
class JSONRPCInterface(BaseInterface):
	def __init__(self,sinfo,**kw):
		def_kw = {
			'service_descriptor': JSONRPCServiceDescriptor,
			'request_handler': JSONRPCRequestHandler,
			'response_handler': JSONRPCResponseHandler,
			'fault_handler': JSONRPCFaultHandler}
		def_kw.update(kw)
		BaseInterface.__init__(self,sinfo,**def_kw)

	@staticmethod
	def _interface_name():
		return 'jsonrpc10'

	@staticmethod
	def _accept_basetype(typ):
		return pytype_support.count(typ)>0

	@staticmethod
	def _accept_list():
		return True

	@staticmethod
	def _accept_dict():
		return False
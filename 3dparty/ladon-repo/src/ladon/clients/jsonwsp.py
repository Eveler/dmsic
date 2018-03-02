#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,json,types,pprint,os,tempfile,re
from optparse import OptionParser,OptionGroup
from ladon.tools.multiparthandler import MultiPartReader, MultiPartWriter
from ladon.types.attachment import attachment
from ladon.compat import PORTABLE_STRING,PORTABLE_STRING_TYPES

if sys.version_info[0]>=3:
	from urllib.parse import urlparse,splitport
	from http.client import HTTPConnection, HTTPSConnection
else:
	from urllib import splitport
	from urlparse import urlparse
	from httplib import HTTPConnection, HTTPSConnection

rx_ctype_charset = re.compile('charset\s*=\s*([-_.a-zA-Z0-9]+)',re.I)
rx_detect_multipart = re.compile('multipart/([^; ]+)',re.I)
rx_detect_boundary = re.compile('boundary=([^; ]+)',re.I)
rx_detect_attachment_ref = re.compile('^cid:(.+)$',re.I)

def probe_charset(headers,default='UTF-8'):
	global rx_ctype_charset
	try:
		res = rx_ctype_charset.findall(headers['CONTENT-TYPE'])
		if len(res):
			return res[0]
		return headers['HTTP-ACCEPT-CHARSET'].split(';')[0].split(',')[0]
	except:
		pass
	
	return default


def fix_attachment(val,attachment_map):
	if hasattr(val,'read'):
		while 1:
			cid = 'file%s' % attachment_map['cid_seq']
			attachment_map['cid_seq'] += 1
			if cid not in attachment_map['files']:
				break
		attachment_map['files'][cid] = val
		return 'cid:%s' % cid
		
	if type(val) in PORTABLE_STRING_TYPES and len(val)>0 and val[0]=='@' and os.path.isfile(val[1:]):
		cid = os.path.normpath(val[1:])
		if cid not in attachment_map:
			attachment_map['files'][cid] = open(cid,'rb')
			return 'cid:%s' % cid
	
	return None


def walk_args_dict(kw,attachment_map):
	for key,val in kw.items():
		if type(val)==tuple:
			val = list(val)
			kw[key] = val
		if type(val)==list:
			for vidx in range(len(val)):
				if type(val[vidx])==dict:
					walk_args_dict(val[vidx],attachment_map)
				else:
					attachment_ref = fix_attachment(val[vidx],attachment_map)
					if not attachment_ref == None:
						val[vidx] = attachment_ref
				
		elif type(val)==dict:
			walk_args_dict(val,attachment_map)
		else:
			attachment_ref = fix_attachment(val,attachment_map)
			if not attachment_ref == None:
				kw[key] = attachment_ref

class JSONWSPResponse(object):
	def __init__(self,status,reason,headers):
		self.response_body = ''
		self.response_dict = {}
		self.headers = headers
		self.status = status
		self.reason = reason
		self.attachments = {}
		self.dict_attachments = []


	def __del__(self):
		self.response_dict = {}
		for a in self.dict_attachments:
			a.bufferobj.close()
			del a

		for cid,a in self.attachments.items():
			fname = a.bufferobj.name
			a.bufferobj.close()
			del a
			os.unlink(fname)


	def check_attachment(self,val):
		global rx_detect_attachment_ref
		if type(val) == PORTABLE_STRING:
			m = rx_detect_attachment_ref.match(val)
			if m and m.groups()[0] in self.attachments:
				a = self.attachments[m.groups()[0]]
				attachment_copy = attachment(open(a.bufferobj.name,'rb'),a.size,a.headers,None)
				self.dict_attachments += [attachment_copy]
				return attachment_copy
		return None

	def walk_result_dict(self,result=None):
		if result==None:
			result = self.response_dict
		for key,val in result.items():
			if result==self.response_dict and key!='result':
				continue
			if type(val)==list:
				for vidx in range(len(val)):
					if type(val[vidx])==dict:
						self.walk_result_dict(val[vidx])
					else:
						attachment = self.check_attachment(val[vidx])
						if not attachment == None:
							val[vidx] = attachment
					
			elif type(val)==dict:
				self.walk_result_dict(val)
			else:
				attachment = self.check_attachment(val)
				if not attachment == None:
					result[key] = attachment


class JSONWSPClient(object):

	def __init__(self,description=None,url=None,debug=False,via_proxy=False,cookies={},headers={}):
		
		self.description_loaded = False
		self.via_proxy = via_proxy
		self.cookie_dict = cookies
		self.header_dict = headers
		
		if description:
			self.parse_url(description)
			self.parse_description()
		if url:
			self.parse_url(url)
		self.debug = debug

	def parse_url(self,url):
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

	def add_cookie(self,name,value):
		if self.cookie_dict == None:
			self.cookie_dict = {}
		self.cookie_dict[name] = value
	
	def remove_cookie(self,name):
		if name in self.cookie_dict:
			self.cookie_dict.pop(name)
			
	def add_header(self,name,value):
		if self.header_dict == None:
			self.header_dict = {}
		self.header_dict[name] = value
	
	def remove_header(self,name):
		if name in self.header_dict:
			self.header_dict.pop(name)
	
	def get_all_headers(self,extra_headers={}):
	
		headerlist = self.header_dict
		if not extra_headers == None:
			headerlist.update(extra_headers)
		
		cookieString = ""
		if not self.cookie_dict == None:
			for key in self.cookie_dict:
				if not cookieString == "":
					cookieString = cookieString + "; ";
				cookieString = cookieString + key+"="+self.cookie_dict[key]
		
		if "Cookie" in headerlist:
			headerlist["Cookie"] = headerlist["Cookie"]+"; "+cookieString
		else:
			headerlist["Cookie"] = cookieString
			
		return headerlist
		
	def call_method(self,method_name,**kw):
		attachment_map={'cid_seq':1,'files':{}}
		extra_headers = None
		if 'extra_headers' in kw:
			extra_headers = kw['extra_headers']
		walk_args_dict(kw,attachment_map)
		if self.description_loaded:
			minfo = self.method_info(method_name)
			mandatory_params = list(minfo['mandatory_params'])
			optional_params = list(minfo['optional_params'])
			for arg in kw.keys():
				if arg in mandatory_params:
					mandatory_params.remove(arg)
			if len(mandatory_params):
				return -1
		data = {
			'methodname': method_name
		}
		if 'mirror' in kw:
			data['mirror'] = kw.pop('mirror')	
		data['args'] = kw
		if len(attachment_map['files']):
			jsonwsp_response = self.post_mp_request(json.dumps(data),attachment_map['files'],extra_headers=extra_headers)
		else:
			jsonwsp_response = self.post_request(json.dumps(data),extra_headers=extra_headers)
		if jsonwsp_response.status==200:
			response_charset = probe_charset(jsonwsp_response.headers)
			jsonwsp_response.response_dict = json.loads(PORTABLE_STRING(jsonwsp_response.response_body,response_charset))
			jsonwsp_response.walk_result_dict()

		return jsonwsp_response


	def list_methods(self):
		return self.jsonwsp_description['methods'].keys()


	def method_info(self,method_name):
		minfo = self.jsonwsp_description['methods'][method_name]
		params = minfo['params']
		mandatory_params = []
		optional_params = []
		params_order = ['']*len(params)
		for pname,pinfo in params.items():
			params_order[pinfo['def_order']-1] = pname
		for pname in params_order:
			pinfo = params[pname]
			if pinfo['optional']:
				optional_params += [pname]
			else:
				mandatory_params += [pname]
			
		return {
			'method_name': method_name,
			'params_order': params_order,
			'mandatory_params': mandatory_params,
			'optional_params': optional_params,
			'params_info': params,
			'doc_lines': minfo['doc_lines'],
			'ret_info': minfo['ret_info']
		}


	def parse_description(self):
		jsonwsp_response = self.post_request("","",via_proxy=self.via_proxy)
		response_charset = probe_charset(jsonwsp_response.headers)
		self.jsonwsp_description = json.loads(PORTABLE_STRING(jsonwsp_response.response_body,response_charset))
		self.parse_url(self.jsonwsp_description['url'])
		for method_name in self.jsonwsp_description['methods'].keys():
			exec("def placeholder(self,**kw):\n\treturn self.call_method('%s',**kw)" % method_name)
			exec("self.%s = types.MethodType(placeholder,self)" % method_name)
		self.description_loaded = True


	def parse_response(self,response):
		headers = dict((k.upper(), v) for k, v in response.getheaders())
		jsonwsp_response = JSONWSPResponse(response.status, response.reason, headers)
		jsonwsp_charset = probe_charset(jsonwsp_response.headers)
		content_type = response.getheader('content-type')
		content_type = content_type.replace('\n','')
		multipart_match = rx_detect_multipart.findall(content_type)
		if len(multipart_match):
			multipart = multipart_match[0]
			boundary_match = rx_detect_boundary.findall(content_type)
			if len(boundary_match):
				boundary = boundary_match[0]
				mpr = MultiPartReader(20000,boundary.encode(jsonwsp_charset),response)
				mpr.read_chunk()
				while not mpr.eos:
					mpr.read_chunk()
				for cid,cinfo in mpr.attachments_by_id.items():
					jsonwsp_response.attachments[PORTABLE_STRING(cid,jsonwsp_charset)] = attachment(open(cinfo['path'],'rb'),cinfo['size'],cinfo['headers'],jsonwsp_charset)
				resdata = mpr.interface_request
				jsonwsp_response.response_body = resdata
		else:
			resdata = response.read()
			jsonwsp_response.response_body = resdata
		return jsonwsp_response


	def post_request(self,data,extra_path="",via_proxy=False,extra_headers=None):
		all_headers = self.get_all_headers(extra_headers)
		headers = {
			"Content-type": "application/json, charset=UTF-8",
			"Accept": "application/json,multipart/related" }
		if via_proxy:
			headers["Ladon-Proxy-Path"] = "%s://%s:%d%s" % (
				self.scheme.lower(),self.hostname,self.port,self.path)
		if self.scheme.lower()=='https':
			conn = HTTPSConnection(self.hostname,self.port)
		else:
			conn = HTTPConnection(self.hostname,self.port)
		req_path = self.path + '/' + extra_path
		if all_headers:
			headers.update(all_headers)
		if req_path.endswith('/description/'):
			print("GET")
			conn.request("GET", req_path, data, headers)
		else:
			conn.request("POST", req_path, data, headers)
		jsonwsp_response = self.parse_response(conn.getresponse())
		conn.close()
		return jsonwsp_response


	def post_mp_request(self,data,files,extra_path="",extra_headers={}):
		# Create the multipart request body
		buffer_fname = tempfile.mktemp()
		buffer_fp = open(buffer_fname,'wb')
		mpw = MultiPartWriter(buffer_fp, header_encoding='utf-8')
		mpw.add_attachment(data.encode('utf-8'),'application/json, charset=UTF-8','body')
		for cid,fp in files.items():
			mpw.add_attachment(fp,'application/octet-stream',cid)
		mpw.done()
		buffer_fp.close()
		headers = {
			"Content-type": b'multipart/related; boundary=' + mpw.boundary,
			"Accept": b'application/json,multipart/related'}
		if self.scheme.lower()=='https':
			conn = HTTPSConnection(self.hostname,self.port)
		else:
			conn = HTTPConnection(self.hostname,self.port)
		req_path = self.path + '/' + extra_path
		buffer_fp = open(buffer_fname,'rb')
		
		all_headers = self.get_all_headers(extra_headers)
		
		if all_headers!=None:
			headers.update(all_headers)
		conn.request("POST", req_path, buffer_fp, headers)
		buffer_fp.close()
		jsonwsp_response = self.parse_response(conn.getresponse())
		conn.close()
		os.unlink(buffer_fname)
		return jsonwsp_response

if __name__=="__main__":
	service_url = sys.argv[1]
	method_name = sys.argv[2]
	cli = JSONWSPClient(service_url)
	if method_name in ['-h','--help']:
		print("\n  "+"\n  ".join(cli.list_methods()))
		sys.exit(0)
	minfo = cli.method_info(method_name)
	mparams = list(minfo['mandatory_params'])
	oparams = list(minfo['optional_params'])
	parser = OptionParser(usage="%s SERVICE_URL METHOD_NAME %s [OPTIONS]" % (sys.argv[0],' '.join(minfo['mandatory_params'])))
	mandatory_group = OptionGroup(parser, "Mandatory argument option-bindings",
		"All mandatory arguments to a service method can be "
		"given via normal arguments, but in some cases it "
		"is nessecary to have option-bindings to an argument "
		"like when using xargs and other commands.")
	optional_group = OptionGroup(parser, "Options","Options for %s" % method_name)
	for p in mparams:
		if minfo['params_info'][p]['type']=='boolean':
			mandatory_group.add_option(
				"--%s"%p.replace('_','-'), 
				dest=p, 
				action="store_true", 
				help='\n'.join(minfo['params_info'][p]['doc_lines']))
		else:
			mandatory_group.add_option(
				"--%s"%p.replace('_','-'),
				dest=p,
				help='\n'.join(minfo['params_info'][p]['doc_lines']))
	parser.add_option_group(mandatory_group)
	for p in oparams:
		if minfo['params_info'][p]['type']=='boolean':
			optional_group.add_option(
				"--%s"%p.replace('_','-'), 
				dest=p, 
				action="store_true", 
				help='\n'.join(minfo['params_info'][p]['doc_lines']))
		else:
			optional_group.add_option(
				"--%s"%p.replace('_','-'),
				dest=p,
				help='\n'.join(minfo['params_info'][p]['doc_lines']))
	parser.add_option_group(optional_group)
	(options, args) = parser.parse_args()
	
	method_call_args = {}

	for p in minfo['optional_params']:
		pval = eval("options.%s" % p)
		if pval != None:
			oparams.remove(p)
			method_call_args[p] = pval

	for p in minfo['mandatory_params']:
		pval = eval("options.%s" % p)
		if pval != None:
			mparams.remove(p)
			method_call_args[p] = pval
	
	if len(sys.argv)<3+len(mparams):
		print("Missing mandatory parameters: %s" % ' '.join(mparams))
		sys.exit(1)
	
	arg_idx = 0
	for arg in args[2:]:
		method_call_args[mparams[arg_idx]] = arg
		arg_idx += 1

	pprint.pprint(eval("cli.%s(**method_call_args)" % method_name).response_dict,indent=2)

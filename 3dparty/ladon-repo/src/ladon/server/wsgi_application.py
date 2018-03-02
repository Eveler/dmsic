# -*- coding: utf-8 -*-
from wsgiref.util import request_uri
import os
import re
import sys
import tempfile
import traceback
import inspect
import types

from ladon import package_root
from ladon.ladonizer.collection import global_service_collection
from ladon.server.dispatcher import Dispatcher
from ladon.server.customresponse import CustomResponse
from ladon.server.default.css import catalog_default_css,service_default_css
from ladon.server.default.templates import catalog_default_template,service_default_template
from ladon.tools.multiparthandler import MultiPartReader, MultiPartWriter
from ladon.interfaces import _interfaces,name_to_interface
from ladon.exceptions.dispatcher import UndefinedInterfaceName,UndefinedService
from ladon.compat import type_to_jsontype,PORTABLE_STRING_TYPES,PORTABLE_STRING
from jinja2 import Template
from docutils.core import publish_parts
from ladon.server import *
import ladon.types.tasktype as tt

if sys.version_info[0]==2:
	from StringIO import StringIO
	from urlparse import parse_qs, urlparse
	def copyFunction(f,fname):
		return types.FunctionType(f.func_code, f.func_globals, name=fname, argdefs=f.func_defaults, closure=f.func_closure)
elif sys.version_info[0]>=3:
	from urllib.parse import parse_qs, urlparse
	from io import StringIO
	def copyFunction(f,fname):
		return types.FunctionType(f.__code__,f.__globals__, name=fname, argdefs=f.__defaults__, closure=f.__closure__)

rx_ctype_charset = re.compile('charset\s*=\s*([-_.a-zA-Z0-9]+)',re.I)
rx_detect_multipart = re.compile('multipart/([^; ]+)',re.I)
rx_detect_boundary = re.compile('boundary=([^; ]+)',re.I)
rx_detect_publisher = re.compile('^@publisher: (\w+).*$',re.I)

def probe_language(env,default=['en']):
	
	langs = []
	acceptlanguage = ""
	contentlanguage = ""
	
	if 'HTTP_ACCEPT_LANGUAGE' in env:
		acceptlanguage = env['HTTP_ACCEPT_LANGUAGE']
	elif 'ACCEPT_LANGUAGE' in env:
		acceptlanguage = env['ACCEPT_LANGUAGE']
		
	if 'HTTP_CONTENT_LANGUAGE' in env:
		contentlanguage = env['HTTP_CONTENT_LANGUAGE']
	elif 'CONTENT_LANGUAGE' in env:
		contentlanguage = env['CONTENT_LANGUAGE']
	
	if not contentlanguage == "":
		langsplit = contentlanguage.split(',')
		for lang in langsplit:
			langcode = lang.split('-')[0].lower()
			if not langcode in langs:
				langs.append(langcode)
	
	if not acceptlanguage == "":
		langsplit = acceptlanguage.split(',')
		for lang in langsplit:
			langcode = lang.split(';')[0].split('-')[0].lower()
			if not langcode in langs:
				langs.append(langcode)
				
	if len(langs) == 0:
		return default
	else:
		return langs
	
def probe_charset(env,default='UTF-8'):
	try:
		global rx_ctype_charset
		res = rx_ctype_charset.findall(env['CONTENT_TYPE'])
		if len(res):
			return res[0]
		return env['HTTP_ACCEPT_CHARSET'].split(';')[0].split(',')[0]
	except:
		return default

def probe_client_path(environ):
	# Simplification of probe_client_path
	# Contributed by: George Marshall
	if 'HTTP_LADON_PROXY_PATH' in environ:
		return environ['HTTP_LADON_PROXY_PATH']
	return request_uri(environ,include_query=0)

def publish_doc(doc_lines):
	if len(doc_lines):
		first_line = doc_lines[0].strip()
		m = rx_detect_publisher.match(first_line)
		publisher = 'raw'
		if m:
			publisher = m.groups()[0]
			doclines = doc_lines[1:]
		else:
			doclines = doc_lines

		if publisher=='docutils':
			return publish_parts('\n'.join(doclines),writer_name='html')['body']
		if publisher=='pre':
			return '<br/>'.join(doclines)
		if publisher=='raw':
			return '\n'.join(doclines)

def read_data_file(start_response,path_info,path_list):
	ext = os.path.splitext(path_info)[1][1:]
	ct = content_types.get(ext.lower(),{}).get('Content-Type', None)
	data = b''
	status = "200 OK"
	if not ct:
		ct = "plain/text"
		status = b"501 Server Error"
		data = b'Unsupported filetype'
	else:
		found = False
		paths = map(lambda x: os.path.join(x,path_info[1:]), path_list)
		for p in paths:
			if os.path.exists(p):
				found = True
				data = open(p,'rb').read()
				break
		if not found:
			ct = "plain/text"
			data = b"File: %s could not be found" % path_info
			status = b"404 Not found"
	response_headers = [
		('Content-Type', ct ),
		('Content-Length', str(len(data)) )
	]
	start_response(status, response_headers)
	return data


class LadonWSGIApplication(object):

	reserved_roots = ['skins']

	def __init__(self,service_list,path_list=None,catalog_name=None,catalog_desc=None,logging=NO_LOGGING):
		self.staticfiles = {
			'catalog.css': {
				'data': catalog_default_css,
				'mtime': 0
			},
			'service.css': {
				'data': service_default_css,
				'mtime': 0
			},
			'catalog.template': {
				'data': catalog_default_template,
				'mtime': 0
			},
			'service.template': {
				'data': service_default_template,
				'mtime': 0
			},
			'skins/catalog-extra.css': {
				'data': '',
				'mtime': 0
			},
			'skins/service-extra.css': {
				'data': '',
				'mtime': 0
			}
		}
		self.skins = {}
		self.logging = logging
		self.catalog_name = catalog_name
		self.catalog_desc = catalog_desc
		if not catalog_name:
			self.catalog_name = "Ladon Service Catalog"
		if not catalog_desc:
			self.catalog_desc = "This is the Ladon Service Catalog. It presents the services exposed by on this particular site. Click on a service name to examine which methods and interfaces it exposes."
		if type(service_list) in PORTABLE_STRING_TYPES:
			self.service_list = [service_list]
		else:
			self.service_list = service_list

		self.path_list = [package_root('resources')]
		if path_list:
			if type(path_list) in PORTABLE_STRING_TYPES:
				self.path_list += [path_list]
			elif type(path_list) in [list,tuple]:
				self.path_list += list(path_list)

		for p in self.path_list:
			if p not in sys.path:
				sys.path += [p]

		self.import_services(self.service_list)
		self.find_custom_service_skins()


	def find_custom_service_skins(self):
		skins = {}
		for p in self.path_list:
			skins_path = os.path.join(p,'skins')
			if os.path.exists(skins_path):
				files = os.listdir(skins_path)
				for f in files:
					skin_path = os.path.join(skins_path,f)
					template_path = os.path.join(skin_path,'service.template')
					css_path = os.path.join(skin_path,'service.css')
					if os.path.isdir(skin_path) and os.path.exists(template_path) and f not in skins:
						skins[f] = skin_path
		self.skins = skins
		return skins


	def update_static(self,staticfile):
		for p in self.path_list:
			staticpath = os.path.join(p,staticfile)
			if os.path.exists(staticpath):
				static_mtime = os.stat(staticpath).st_mtime
				if staticfile not in self.staticfiles or static_mtime > self.staticfiles[staticfile]['mtime']:
					self.staticfiles[staticfile] = {}
					self.staticfiles[staticfile]['mtime'] = static_mtime
					self.staticfiles[staticfile]['data'] = open(staticpath).read()
				return True
			else:
				continue
		return False


	def generate_catalog_html(self,services,client_path,catalog_name,catalog_desc,charset,languages,skin):
		css_path = 'catalog.css'
		template_path = 'catalog.template'
		self.update_static('skins/catalog-extra.css')
		if skin:
			css_path = 'skins/%s/catalog.css' % skin
			template_path = 'skins/%s/catalog.template' % skin
			if not self.update_static(template_path):
				css_path = 'catalog.css'
				template_path = 'catalog.template'
				self.update_static(template_path)
				self.update_static(css_path)
			self.update_static(css_path)
		else:
			self.update_static(template_path)
			self.update_static(css_path)

		fix_path = urlparse(client_path)
		pretty_client_path = '%s://%s%s' % (fix_path.scheme,fix_path.netloc,fix_path.path)
		if pretty_client_path[-1:]=='/':
			pretty_client_path = pretty_client_path[:-1]
		catalog_info = {
			'catalog_name': catalog_name,
			'catalog_desc': catalog_desc,
			'css': self.staticfiles['catalog.css']['data'],
			'extra_css': self.staticfiles['skins/catalog-extra.css']['data'],
			'client_path': pretty_client_path,
			'query_string': fix_path.query,
			'charset': charset,
			'languages': languages,
			'services': services.values()
		}

		template = Template(self.staticfiles['catalog.template']['data'])
		return template.render(catalog_info).encode(charset)


	def generate_service_html(self,service,client_path,charset,languages,skin=None):
		def get_ladontype(typ):
			if type(typ)==list:
				if typ[0] in service.typemanager.type_dict:
					return typ[0].__name__
				else:
					return False
			else:
				if typ in service.typemanager.type_dict:
					return typ.__name__
				else:
					return False

		def type_to_string(typ):
			paramtype = typ
			if type(paramtype)==list:
				paramtype = paramtype[0]
				if paramtype in service.typemanager.type_dict:
					paramtype_str = '[ %s ]' % paramtype.__name__
				else:
					paramtype_str = '[ %s ]' % type_to_jsontype[paramtype]
			else:
				if paramtype in service.typemanager.type_dict:
					paramtype_str = paramtype.__name__
				elif paramtype in type_to_jsontype:
					paramtype_str = type_to_jsontype[paramtype]
				else:
					paramtype_str = paramtype.__name__
			return paramtype_str

		fix_path = urlparse(client_path)
		css_path = 'service.css'
		template_path = 'service.template'
		self.update_static('skins/service-extra.css')
		if skin:
			css_path = 'skins/%s/service.css' % skin
			template_path = 'skins/%s/service.template' % skin
			if not self.update_static(template_path):
				css_path = 'service.css'
				template_path = 'service.template'
				self.update_static(template_path)
				self.update_static(css_path)
			self.update_static(css_path)
		else:
			self.update_static(template_path)
			self.update_static(css_path)

		service_info = {
			'servicename': service.servicename,
			'doc_lines': service.doc_lines,
			'doc': publish_doc(service.doc_lines),
			'interfaces': _interfaces.keys(),
			'methods': [],
			'types': [],
			'css': self.staticfiles.get(css_path,{}).get('data',None),
			'extra_css': self.staticfiles['skins/service-extra.css']['data'],
			'client_path': client_path,
			'query_string': fix_path.query,
			'charset': charset,
			'languages': languages,
			'skins': list(self.skins.keys()),
			'current_skin': skin
		}
		for method in service.method_list():
			method_info = {
				'methodname': method.name(),
				'params': [],
				'doc': publish_doc(method._method_doc),
				'returns': {
					'type': type_to_string(method._rtype),
					'ladontype': get_ladontype(method._rtype),
					'doc': publish_doc(method._rtype_doc),
					'doc_lines': method._rtype_doc } }
			for param in method.args():
				param_info = {
					'name': param['name'],
					'type': type_to_string(param['type']),
					'ladontype': get_ladontype(param['type']),
					'optional': param['optional'],
					'doc': publish_doc(param['doc']),
					'doc_lines': param['doc'] }
				if 'default' in param:
					default_type = param['default']
					if param['type'] in PORTABLE_STRING_TYPES:
						param_info['default'] = '"%s"' % param['default']
					else:
						param_info['default'] = str(param['default'])
				method_info['params'] += [ param_info ]
			service_info['methods'] += [method_info]

		types = service_info['types']
		type_order = service.typemanager.type_order
		for typ in type_order:
			if type(typ)==dict:
				desc_type = {}
				desc_type['name'] = typ['name']
				desc_type['attributes'] = {}
				for k,v,props in typ['attributes']:
					desc_type_val = type_to_string(v)
					desc_type['attributes'][k] = {
						'type': desc_type_val,
						'props': props,
						'ladontype': get_ladontype(v) }
				types += [desc_type]

		template = Template(self.staticfiles[template_path]['data'])
		return template.render(service_info).encode(charset)

	def import_services(self,service_list):
		# Fix that eliminates the need for exec()
		# contributed by: Tamás Gulácsi
		for service in service_list:
			m = __import__(service)
			sfile = inspect.getsourcefile(m)
			for skey, smi in global_service_collection().services.items():
				for method_name,lmi in list(smi.methods.items()):
					task_rtype = getattr(lmi,'_task_rtype',None)
					if task_rtype!=None:
						if skey[0]==sfile:
							cls = getattr(m,skey[1])
							setattr(cls,"%s_progress" % method_name, tt.taskProgress)
							lmi.sinfo.add_method(tt.taskProgress,*(int,),**dict(list(tt.taskProgress_kw.items()) + [('override_method_name',"%s_progress" % method_name)]))
							setattr(cls,"%s_result" % method_name, tt.taskResult)
							lmi.sinfo.add_method(tt.taskResult,*(int,),**{'override_method_name': "%s_result" % method_name,'rtype':task_rtype})
							setattr(cls,"_task_%s" % method_name, copyFunction(getattr(cls,method_name),"_task_%s" % method_name))
							setattr(cls,method_name, copyFunction(tt.taskStarter,method_name))
	
	def parse_environ(self,environ):
		global rx_detect_multipart,rx_detect_boundary
		path_parts = []
		path_info=['']
		if 'PATH_INFO' in environ:
			path_info = environ['PATH_INFO'].strip().split('/')
		if path_info[0]=='':
			path_info = path_info[1:]
		for p in path_info:
			if p.strip():
				path_parts += [p]

		# path based schema
		sname = ifname = action = None
		if len(path_parts)>0:
			sname = path_parts[0]
		if len(path_parts)>1:
			ifname = path_parts[1]
		if len(path_parts)>2:
			action = path_parts[2]

		# Multipart detection
		multipart = boundary = None
		if 'CONTENT_TYPE' in environ:
			content_type = environ['CONTENT_TYPE']
			content_type = content_type.replace('\n','')
			multipart_match = rx_detect_multipart.findall(content_type)
			if len(multipart_match):
				multipart = multipart_match[0]
				boundary_match = rx_detect_boundary.findall(content_type)
				if len(boundary_match):
					boundary = boundary_match[0]
		return sname,ifname,action,multipart,boundary

	def __call__(self,environ, start_response):
		status = '200 OK'
		response_headers = []
		content_type = 'text/plain'
		output = ''
		charset = probe_charset(environ,default='UTF-8')
		languages = probe_language(environ,default=['en'])
		
		try:
			fault_hint = 'Processing request (further details)'
			sname,ifname,action,multipart,boundary = self.parse_environ(environ)
			client_path = probe_client_path(environ)
			query = parse_qs(environ['QUERY_STRING'])
			if sname in self.reserved_roots:
				fault_hint = 'Attempting to fetch server-side static skin-data at location: "%s"' % environ['PATH_INFO']
				if sname=='skins':
					data = read_data_file(start_response,environ['PATH_INFO'],self.path_list)
					return [ data ]

			sinst = ifclass = None
			if ifname:
				fault_hint = 'Searching for the interface called "%s"' % ifname
				ifclass = name_to_interface(ifname)
				if not ifclass:
					raise UndefinedInterfaceName(ifname,'The interface name "%s" has not been defined' % ifname)

			if sname:
				fault_hint = 'Searching for the service-class: "%s"' % sname
				service_search = global_service_collection().services_by_name(sname)
				if not len(service_search):
					raise UndefinedService(ifname,'Service "%s" has not been exposed' % sname)
				sinst = service_search[0]

			dispatcher = None
			if sinst and ifclass:
				fault_hint = 'Instantiating dispatcher for "%s"' % sname
				dispatcher = Dispatcher(sinst,ifclass,charset,languages,self.logging)
			elif not sname:
				fault_hint = 'Generating service catalog'
				content_type = 'text/html'
				skin = query.get('skin', [None])[0]
				output = self.generate_catalog_html(
					global_service_collection().services,
					client_path,
					self.catalog_name,
					self.catalog_desc,charset,languages,skin)
			elif sinst and not ifname:
				fault_hint = 'Generating service API HTML for "%s"' % sname
				content_type = 'text/html'
				skin = query.get('skin', [None])[0]
				output = self.generate_service_html(
					sinst,
					client_path,
					charset, 
					languages,skin)

			if dispatcher and dispatcher.iface:
				if action=='description':
					fault_hint = 'Generating "%s" description for "%s"' % (ifname,sname)
					content_type = dispatcher.iface.description_content_type()
					service_url = client_path[0:client_path.find('/description')]
					output += dispatcher.iface.description(service_url,charset,**dict(map(lambda x: (x[0],x[1][0]), query.items())))
				else:
					fault_hint = 'Checking method call request via "%s" on "%s"' % (ifname,sname)
					allowed_methods = ['POST']
					if environ['REQUEST_METHOD'] not in allowed_methods or not environ.get('CONTENT_LENGTH', ''):
						message = 'Requests for %s %s interface must be posted' % (sname,ifname)
						status = '405 %s' % message
						response_headers.append(('Allow', ','.join(allowed_methods)))
						output += message
					else:
						fault_hint = 'Preparing "%s" call to "%s"' % (ifname,sname)
						content_type = dispatcher.iface.response_content_type()
						content_length = int(environ['CONTENT_LENGTH'])
						if multipart and boundary:
							fault_hint = 'Parsing incoming multipart request and attachments'
							mph = MultiPartReader(20000,boundary.encode(charset),environ['wsgi.input'],content_length)
							mph.read_chunk()
							while not mph.eos:
								mph.read_chunk()
							encapsulated_charset = probe_charset(mph.interface_request_headers,default=None)
							request_data = mph.interface_request
							if encapsulated_charset:
								# If a specific charset is/usr/local/bin/rdesktop specified for the interface request multipart
								# let this charset superseed the charset globally specified for the request.
								dispatcher.response_encoding = encapsulated_charset

							environ['attachments'] = mph.attachments
							environ['attachments_by_id'] = mph.attachments_by_id
						else:
							request_data = environ['wsgi.input'].read(content_length)
						fault_hint = 'Passing request on to the dispatcher'
						response_part = dispatcher.dispatch_request(request_data,environ)
						if isinstance(response_part,CustomResponse):
							response_headers += response_part.response_headers()
							start_response(status, response_headers)
							return response_part.response_data()
						elif len(environ['response_attachments'].attachments_by_cid):
							# Attachments present - Send multipart response
							response_temp_fname = tempfile.mktemp()
							temp_buffer = open(response_temp_fname,'wb')
							mpw = MultiPartWriter(temp_buffer, header_encoding=charset)
							mpw.add_attachment(response_part,'%s, charset=%s' % (content_type,charset),'rpc-part')
							for cid,a in environ['response_attachments'].attachments_by_cid.items():
								mpw.add_attachment(a,'application/octet-stream',cid,a.headers)
							mpw.done()
							temp_buffer.close()
							content_length = str(os.stat(response_temp_fname).st_size)
							output = open(response_temp_fname,'rb')
							if sys.version_info[0]==2:
								content_type = "multipart/related; boundary=" + mpw.boundary
							elif sys.version_info[0]>=3:
								content_type = "multipart/related; boundary=" + str(mpw.boundary,'iso-8859-1')

						else:
							# No attachments - Send normal response
							output = response_part

			if 'attachments' in environ:
				for a_id,a_info in environ['attachments'].items():
					if os.path.exists(a_info['path']):
						os.unlink(a_info['path'])

		except Exception as e:
			status = '500 An Error occured while processing the request'
			content_type = 'text/plain'
			strio = StringIO()
			traceback.print_exc(file=strio)
			output = strio.getvalue()
			output += "\nHint: " + fault_hint

		if not hasattr(output,'read'):
			# not file-like object
			content_length = str(len(output))

		response_headers += [
			('Content-Type', "%s; charset=%s" % (content_type,charset)),
			('Content-Length', content_length)
		]
		start_response(status, response_headers)

		if hasattr(output,'read'):
			# File-like object
			block_size = 4096
			if 'wsgi.file_wrapper' in environ:
				return environ['wsgi.file_wrapper'](output, block_size)
			else:
				return iter(lambda: output.read(block_size), '')

		if sys.version_info[0]>=3:
			# Python 3 support
			if type(output)==str:
				output = bytes(output,charset)

		return [output]


# -*- coding: utf-8 -*-

from ladon.interfaces.base import BaseInterface,ServiceDescriptor,BaseRequestHandler,BaseResponseHandler,BaseFaultHandler
from ladon.interfaces import expose
from ladon.compat import PORTABLE_STRING,type_to_xsd,pytype_support,BytesIO
from xml.sax.handler import ContentHandler,feature_namespaces
from xml.sax import make_parser
from xml.sax.xmlreader import InputSource
import sys,re,traceback

rx_nil_attr = re.compile(PORTABLE_STRING('^\w*[:]{0,1}nil$'),re.I)

class SOAPServiceDescriptor(ServiceDescriptor):
	
	xsd_type_map = type_to_xsd
	_content_type = 'text/xml'
	
	def generate(self,servicename,servicenumber,typemanager,methodlist,service_url,encoding):
		"""
		Generate WSDL file for SOAPInterface
		"""
		type_dict = typemanager.type_dict
		type_order = typemanager.type_order

		def map_type(typ):
			if typ in SOAPServiceDescriptor.xsd_type_map:
				return SOAPServiceDescriptor.xsd_type_map[typ]
			else:
				return typ.__name__

		import xml.dom.minidom as md
		doc = md.Document()
		
		# SERVICE DEFINITION
		# Create the definitions element for the service
		definitions = doc.createElement('definitions')
		definitions.setAttribute('xmlns:SOAP','http://schemas.xmlsoap.org/wsdl/soap/')
		definitions.setAttribute('xmlns:WSDL','http://schemas.xmlsoap.org/wsdl/')
		definitions.setAttribute('xmlns:mime','http://schemas.xmlsoap.org/wsdl/mime/')
		definitions.setAttribute('name', servicename)
		definitions.setAttribute('targetNamespace','urn:%s' % servicename)
		definitions.setAttribute('xmlns:tns','urn:%s' % servicename)
		definitions.setAttribute('xmlns:SOAP-ENV','http://schemas.xmlsoap.org/soap/envelope/')
		definitions.setAttribute('xmlns:SOAP-ENC','http://schemas.xmlsoap.org/soap/encoding/')
		definitions.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
		definitions.setAttribute('xmlns:xsd','http://www.w3.org/2001/XMLSchema')
		definitions.setAttribute('xmlns:ns%d' % servicenumber,'urn:%s' % servicename)
		definitions.setAttribute('xmlns','http://schemas.xmlsoap.org/wsdl/')
		doc.appendChild(definitions)
		
		# TYPES
		# The types element
		types = doc.createElement('types')
		definitions.appendChild(types)
		
		# Service schema for types required by the target namespace we defined in the definition element
		schema = doc.createElement('schema')
		schema.setAttribute('targetNamespace','urn:%s' % servicename)
		schema.setAttribute('xmlns:SOAP-ENV','http://schemas.xmlsoap.org/soap/envelope/')
		schema.setAttribute('xmlns:SOAP-ENC','http://schemas.xmlsoap.org/soap/encoding/')
		schema.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
		schema.setAttribute('xmlns:xsd','http://www.w3.org/2001/XMLSchema')
		schema.setAttribute('xmlns:ns%d' % servicenumber,'urn:%s' % servicename)
		schema.setAttribute('xmlns','http://www.w3.org/2001/XMLSchema')
		types.appendChild(schema)
		
		# Import namespace schema
		import_tag = doc.createElement('import')
		import_tag.setAttribute('namespace','http://schemas.xmlsoap.org/soap/encoding/')
		schema.appendChild(import_tag)

		# Define types, the type_order variable holds all that need to be defined and in the
		# correct order.
		# * If a list is encountered as a type it will be handled as a complex type with a single element reflecting the inner type.
		# * LadonTypes (identified by being contained in type_dict) are also handled as complex types with an element-tag per attribute
		# * Primitive types (either as LadonType attributes or list inner-types) are added as xsd - SOAP types.
		for typ in type_order:
			if isinstance(typ, list):
				inner = typ[0]
				complextype = doc.createElement('complexType')
				complextype.setAttribute('name','ArrayOf%s' % inner.__name__)
				schema.appendChild(complextype)
				complexcontent = doc.createElement('complexContent')
				complextype.appendChild(complexcontent)
				restriction = doc.createElement('restriction')
				restriction.setAttribute('base','SOAP-ENC:Array')
				complexcontent.appendChild(restriction)
				sequence = doc.createElement('sequence')
				element = doc.createElement('element')
				element.setAttribute('name','item')
				if inner in type_dict:
					element.setAttribute('type','ns%d:%s' % (servicenumber,inner.__name__))
				else:
					element.setAttribute('type','xsd:%s' % map_type(inner))
				element.setAttribute('minOccurs','0')
				element.setAttribute('maxOccurs','unbounded')
				sequence.appendChild(element)
				restriction.appendChild(sequence)
				attribute = doc.createElement('attribute')
				attribute.setAttribute('ref','SOAP-ENC:arrayType')
				if inner in type_dict:
					attribute.setAttribute('WSDL:arrayType','ns%d:%s[]' % (servicenumber,inner.__name__))
				else:
					attribute.setAttribute('WSDL:arrayType','xsd:%s[]' % map_type(inner))
				restriction.appendChild(attribute)
				
			else:
				complextype = doc.createElement('complexType')
				complextype.setAttribute('name',typ['name'])
				schema.appendChild(complextype)
				sequence = doc.createElement('sequence')
				complextype.appendChild(sequence)
				for k,v,props in typ['attributes']:
					element = doc.createElement('element')
					element.setAttribute('name',k.replace('_','-'))
					element.setAttribute('maxOccurs','1')
					element.setAttribute('minOccurs','1')
					if props.get('nullable')==True:
						element.setAttribute('minOccurs','0')
						element.setAttribute('nillable','true')
					if isinstance(v, list):
						inner = v[0]
						element.setAttribute('type','ns%d:ArrayOf%s' % (servicenumber,inner.__name__))
						element.setAttribute('minOccurs','0')
						element.setAttribute('nillable','true')
					else:
						if v in type_dict:
							element.setAttribute('type','ns%d:%s' % (servicenumber,v.__name__))
						else:
							element.setAttribute('type','xsd:%s' % map_type(v))
					sequence.appendChild(element)

		#<complexType name="ArrayOfstring">
		#<complexContent>
		#<restriction base="SOAP-ENC:Array">
		#<sequence>
		#<element name="attr" type="xsd:string" minOccurs="0" maxOccurs="unbounded"/>
		#</sequence>
		#<attribute ref="SOAP-ENC:arrayType" WSDL:arrayType="xsd:string[]"/>
		#</restriction>
		#</complexContent>
		#</complexType>

		#<message name="listUserRoles">
		#<part name="session-id" type="xsd:string"/>
		#<part name="domain" type="xsd:string"/>
		#<part name="uid" type="xsd:string"/>
		#</message>

		#<message name="listUserRolesResponse">
		#<part name="capa-res" type="ns2:CapaResult"/>
		#<part name="roles" type="ns2:ArrayOfRoleInfo"/>
		#</message>

		for m in methodlist:
			message = doc.createElement('message')
			message.setAttribute('name',m.name())
			definitions.appendChild(message)
			for arg in m.args():
				part = doc.createElement('part')
				part.setAttribute('name',arg['name'].replace('_','-'))
				if isinstance(arg['type'], (list, tuple)):
					part.setAttribute('type','ns%d:ArrayOf%s' % (servicenumber,arg['type'][0].__name__))
				else:
					if arg['type'] in type_dict:
						part.setAttribute('type','ns%d:%s' % (servicenumber,arg['type'].__name__))
					else:
						part.setAttribute('type','xsd:%s' % map_type(arg['type']))
				message.appendChild(part)
			message = doc.createElement('message')
			message.setAttribute('name',"%sResponse" % m.name())
			definitions.appendChild(message)
			if isinstance(m._rtype, (list, tuple)):
				part = doc.createElement('part')
				part.setAttribute('name','result')
				part.setAttribute('type','ns%d:ArrayOf%s' % (servicenumber,m._rtype[0].__name__))
				message.appendChild(part)
			elif m._rtype in type_dict:
				for k,v,props in type_dict[m._rtype]['attributes']:
					part = doc.createElement('part')
					part.setAttribute('name',k.replace('_','-'))
					#part.setAttribute('maxOccurs','1')
					if isinstance(v, list):
						inner = v[0]
						part.setAttribute('type','ns%d:ArrayOf%s' % (servicenumber,inner.__name__))
						#part.setAttribute('minOccurs','0')
						#part.setAttribute('nillable','true')
					else:
						if v in type_dict:
							part.setAttribute('type','ns%d:%s' % (servicenumber,v.__name__))
						else:
							part.setAttribute('type','xsd:%s' % map_type(v))
						#part.setAttribute('minOccurs','1')
					message.appendChild(part)
			else:
				part = doc.createElement('part')
				part.setAttribute('name','result')
				part.setAttribute('type','xsd:%s' % map_type(m._rtype))
				message.appendChild(part)

		#<portType name="userservicePortType">
		#<operation name="createUser">
		#<documentation>Service definition of function ns2__createUser</documentation>
		#<input message="tns:createUser"/>
		#<output message="tns:createUserResponse"/>
		#</operation>
		porttype = doc.createElement('portType')
		porttype.setAttribute('name','%sPortType' % servicename)
		definitions.appendChild(porttype)

		for m in methodlist:
			operation = doc.createElement('operation')
			operation.setAttribute('name',m.name())
			porttype.appendChild(operation)
			if m.__doc__:
				documentation = doc.createElement('documentation')
				documentation.appendChild(doc.createTextNode(m.__doc__))
				operation.appendChild(documentation)
			input_tag = doc.createElement('input')
			input_tag.setAttribute('message','tns:%s' % m.name())
			operation.appendChild(input_tag)
			output_tag = doc.createElement('output')
			output_tag.setAttribute('message','tns:%sResponse' % m.name())
			operation.appendChild(output_tag)



		#<binding name="userservice" type="tns:userservicePortType">
		#<SOAP:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>
		#<operation name="createUser">
		#<SOAP:operation style="rpc" soapAction=""/>
		#<input>
		#<SOAP:body use="encoded" namespace="urn:userservice" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
		#</input>
		#<output>
		#<SOAP:body use="encoded" namespace="urn:userservice" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
		#</output>
		#</operation>

		binding = doc.createElement('binding')
		binding.setAttribute('name',servicename)
		binding.setAttribute('type',"tns:%sPortType" % servicename)
		transport = doc.createElement('SOAP:binding')
		transport.setAttribute('style','rpc')
		transport.setAttribute('transport','http://schemas.xmlsoap.org/soap/http')
		binding.appendChild(transport)
		definitions.appendChild(binding)

		for m in methodlist:
			operation = doc.createElement('operation')
			operation.setAttribute('name',m.name())
			binding.appendChild(operation)
			soapaction = doc.createElement('SOAP:operation')
			soapaction.setAttribute('style','rpc')
			soapaction.setAttribute('soapAction',"%s/%s" % (service_url,m.name()))
			operation.appendChild(soapaction)
			
			m._multipart_response_required
			input_tag = doc.createElement('input')
			body_parent = input_tag
			if m._multipart_request_required:
				multipart_related = doc.createElement('mime:multipartRelated')
				mime_body_part = doc.createElement('mime:part')
				body_parent = mime_body_part
				mime_content_part = doc.createElement('mime:part')
				mime_content = doc.createElement('mime:content')
				mime_content.setAttribute('type','*/*')
				input_tag.appendChild(multipart_related)
				multipart_related.appendChild(mime_body_part)
				multipart_related.appendChild(mime_content_part)
				mime_content_part.appendChild(mime_content)
				
			input_soapbody = doc.createElement('SOAP:body')
			input_soapbody.setAttribute('use','encoded')
			input_soapbody.setAttribute('namespace','urn:%s' % servicename)
			input_soapbody.setAttribute('encodingStyle','http://schemas.xmlsoap.org/soap/encoding/')
			body_parent.appendChild(input_soapbody)
			operation.appendChild(input_tag)
			output_tag = doc.createElement('output')
			body_parent = output_tag
			if m._multipart_request_required:
				multipart_related = doc.createElement('mime:multipartRelated')
				mime_body_part = doc.createElement('mime:part')
				body_parent = mime_body_part
				mime_content_part = doc.createElement('mime:part')
				mime_content = doc.createElement('content:part')
				mime_content.setAttribute('type','*/*')
				output_tag.appendChild(multipart_related)
				multipart_related.appendChild(mime_body_part)
				multipart_related.appendChild(mime_content_part)
				mime_content_part.appendChild(mime_content)

			output_soapbody = doc.createElement('SOAP:body')
			output_soapbody.setAttribute('use','encoded')
			output_soapbody.setAttribute('namespace','urn:%s' % servicename)
			output_soapbody.setAttribute('encodingStyle','http://schemas.xmlsoap.org/soap/encoding/')
			body_parent.appendChild(output_soapbody)
			operation.appendChild(output_tag)


		#<service name="userservice">
		#<documentation>gSOAP 2.7.10 generated service definition</documentation>
		#<port name="userservice" binding="tns:userservice">
		#<SOAP:address location="http://127.0.0.1:8443/userservice"/>
		#</port>
		#</service>

		service = doc.createElement('service')
		service.setAttribute('name',servicename)
		documentation = doc.createElement('documentation')
		documentation.appendChild(doc.createTextNode('Ladon generated service definition'))
		service.appendChild(documentation)
		port = doc.createElement('port')
		port.setAttribute('name',servicename)
		port.setAttribute('binding','tns:%s' % servicename)
		service.appendChild(port)
		address = doc.createElement('SOAP:address')
		address.setAttribute('location',service_url)
		port.appendChild(address)
		definitions.appendChild(service)
		if sys.version_info[0]>=3:
			return doc.toxml()
		return doc.toxml(encoding)


def u(instring):
	if sys.version_info[0]==2:
		return PORTABLE_STRING(instring,'utf-8')
	else:
		return PORTABLE_STRING(instring)

class ContainerSetRef(object):
	def __init__(self,c,refval):
		self.c = c
		self.refval = refval
	
	def set(self,val):
		self.c[self.refval] = val

class SOAPContentHandler(ContentHandler):
	# Define relevant XML parser states
	ENVELOPE_IN = 1
	HEADER_IN = 2
	BODY_IN = 3
	METHOD_IN = 4
	ARGS_IN = 5
	ARGS_OUT = 6

	def __init__(self,parser):
		"""
		Initialize
		"""
		self.parser = parser
		self.depth = 0
		self.method_depth = -1
		self.state = None
		self.req_dict = {'args':{}}
		self.current_arg_object = self.req_dict['args']
		self.arg_object_stack = []
		self.arg_tagname_stack = []
		self.prev_depth = None
		self.in_cdata = False
		self.multi_ref_hrefs = {}
		self.multi_ref_ids = {}
		self.cur_id_depth = None
		self.cur_id_val = None
		
	def startCdataSection(self):
		"""
		Mark that parser is in CDATA Section.
		"""
		self.in_cdata = True

	def endCdataSection(self):
		"""
		Mark that parser stepped out of a CDATA Section.
		"""
		self.in_cdata = False

	def startDocument(self):
		"""
		Setup XMLParser callbacks, callbacks are setup here as the XMLParser
		is not initialized by XMLReader before it starts parsing.
		"""
		self.parser._parser.StartCdataSectionHandler = self.startCdataSection
		self.parser._parser.EndCdataSectionHandler = self.endCdataSection

	def endDocument(self):
		for id_val,v in self.multi_ref_hrefs.items():
			if id_val in self.multi_ref_ids:
				v.set(self.multi_ref_ids[id_val])
	
	def startElement(self,name,attrs):
		"""
		Handle element entrance.
		"""
		# FIXME: qucik fix for name conversion
		is_null = False
		href_val,id_val = None,None
		for ak,av in attrs.items():
			if rx_nil_attr.match(ak) and av.lower()=='true':
				is_null = True
			elif ak.lower()=='href':
				href_val = av[1:]
			elif ak.lower()=='id':
				self.cur_id_val = av
				self.cur_id_depth = self.depth
				self.multi_ref_ids[av] = {}
				self.current_arg_object = self.multi_ref_ids[av]

		name = name.replace('-', '_')
		# Split element tag into tagname and prefix if nessecary.
		m = name.split(':')
		if len(m)>1:
			prefix,tagname = m
		else:
			prefix,tagname = [''] + m
		# Detect key positions in the SOAP envolope updating the parse pregress state.
		if not self.depth and tagname.lower()=='envelope':
			self.state = self.ENVELOPE_IN
		elif self.state == self.ENVELOPE_IN and tagname.lower()=='header':
			self.state = self.HEADER_IN
		elif self.state in [ self.HEADER_IN,self.ENVELOPE_IN ] and tagname.lower()=='body':
			self.state = self.BODY_IN
		elif self.state == self.BODY_IN:
			# Stepping into the method-name tag.
			self.state = self.METHOD_IN
			self.req_dict['methodname'] = tagname
			self.method_depth = self.depth
		elif self.state == self.METHOD_IN:
			# Stepping into the arguments section.
			self.state = self.ARGS_IN
		
		if self.state == self.ARGS_IN or self.cur_id_val:
			# Starting the argument parsing.
			self.pickup_content = u('')
			
			if is_null:
				newobject = None
			else:
				newobject = {}
			if tagname.lower() == 'item':
				# If the tagname "item" is intercepted it means that we are looking at an array.
				# Therefore the parent dict must be re-assigned to a list object and all objects
				# that follow (until the parser steps out of the item tag) be appended to this
				# list. Lists are ignored by the stack of objects and tagnames
				parent_tagname = self.arg_tagname_stack[-1:][0]
				parent_object = self.arg_object_stack[-1:][0]
				if isinstance(parent_object[parent_tagname], dict):
					# first child object
					parent_object[parent_tagname] = [newobject]
				else:
					# 2nd, 3rd ...
					parent_object[parent_tagname] += [newobject]
				if href_val:
					self.multi_ref_hrefs[href_val] = ContainerSetRef(parent_object,len(parent_object)-1)
			else:
				# Append to the stacks
				self.current_arg_object[tagname] = newobject
				self.arg_object_stack.append(self.current_arg_object)
				self.arg_tagname_stack.append(tagname)
				if href_val:
					self.multi_ref_hrefs[href_val] = ContainerSetRef(self.current_arg_object,tagname)
			self.current_arg_object = newobject
			self.prev_depth = self.depth
		self.depth += 1


	def endElement(self,name):
		# FIXME: qucik fix for name conversion
		name = name.replace('-', '_')
		self.depth -= 1
		# Split element tag into tagname and prefix if nessecary.
		m = name.split(':')
		if len(m)>1:
			prefix,tagname = m
		else:
			prefix,tagname = [''] + m
		# Stop collecting arguments when the parser steps out of the method-name tag.
		if self.depth==self.method_depth:
			# State ARGS_OUT means done parsing arguments.
			self.state = self.ARGS_OUT
		# In all other occations than tagname=='item' pop the stack of argument objects and tagnames.
		if self.depth==self.cur_id_depth:
			if len(self.multi_ref_ids[self.cur_id_val].items()[0][1]):
				self.multi_ref_ids[self.cur_id_val] = self.multi_ref_ids[self.cur_id_val].items()[0][1]
			else:
				self.multi_ref_ids[self.cur_id_val] = self.pickup_content
			self.cur_id_val = None
			self.cur_id_depth = None
		if self.state == self.ARGS_IN or self.cur_id_val:
			if not tagname.lower()=='item':
				if self.depth == self.prev_depth:
					# If parser is stepping out of the element it previously entered it means that
					# there were no child elements, therefore content in between becomes actual
					# argument data.
					parent_tagname = self.arg_tagname_stack[-1:][0]
					parent_object = self.arg_object_stack[-1:][0]
					if not parent_object[parent_tagname]==None:
						parent_object[parent_tagname] = self.pickup_content
				# pop stack of argument objects and tagnames.
				self.current_arg_object = self.arg_object_stack.pop()
				self.arg_tagname_stack.pop()
			else:
				# If list object is empty it must be a primitive, so replace
				# dict with pickup_content
				parent_tagname = self.arg_tagname_stack[-1:][0]
				parent_object = self.arg_object_stack[-1:][0]
				if len(parent_object[parent_tagname][-1:][0])==0:
					parent_object[parent_tagname][-1:] = [self.pickup_content]


	def characters(self,content):
		# Collect data continuosly, reset every time a new element is entered.
		# If it has been detected that the parser is in a CDATA Section all content
		# will be collected as is (raw) otherwise content is stripped.
		if self.state == self.ARGS_IN or self.cur_id_val:
			if self.in_cdata:
				# in CDATA Section
				self.pickup_content += content
			else:
				self.pickup_content += content.strip()


class SOAPRequestHandler(BaseRequestHandler):
	
	def parse_request(self,soap_body,sinfo,encoding):
		parser = make_parser()
		ch = SOAPContentHandler(parser)
		parser.setContentHandler(ch)
		inpsrc = InputSource()
		inpsrc.setByteStream(BytesIO(soap_body))
		parser.parse(inpsrc)
		return ch.req_dict


class SOAPResponseHandler(BaseResponseHandler):
	
	_content_type = 'text/xml'
	_stringify_res_dict = True
	
	@staticmethod
	def value_to_soapxml(value,parent,doc,is_toplevel=False):
		if isinstance(value, dict):
			for attr_name,attr_val in value.items():
				xml_attr_name = attr_name.replace('_','-')
				attr_elem = doc.createElement(xml_attr_name)
				parent.appendChild(attr_elem)
				SOAPResponseHandler.value_to_soapxml(attr_val,attr_elem,doc)
		else:
			if is_toplevel:
				value_parent = doc.createElement('result')
				parent.appendChild(value_parent)
			else:
				value_parent = parent

			if isinstance(value, (list, tuple)):
				if not len(value):
					# Translate empty response arrays to SOAP Null (xsi:nil) value
					value_parent.setAttribute('xsi:nil','true')
				else:
					for item in value:
						item_element = doc.createElement('item')
						SOAPResponseHandler.value_to_soapxml(item,item_element,doc)
						value_parent.appendChild(item_element)
			else:
				if value==None:
					# Set xsi:nil to true if value is None
					value_parent.setAttribute('xsi:nil','true')
				else:
					value_parent.appendChild(doc.createTextNode(value))

	
	def build_response(self,res_dict,sinfo,encoding):
		import xml.dom.minidom as md
		doc = md.Document()
		envelope = doc.createElement('SOAP-ENV:Envelope')
		envelope.setAttribute('xmlns:SOAP-ENV','http://schemas.xmlsoap.org/soap/envelope/')
		envelope.setAttribute('xmlns:SOAP-ENC','http://schemas.xmlsoap.org/soap/encoding/')
		envelope.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
		envelope.setAttribute('xmlns:xsd','http://www.w3.org/2001/XMLSchema')
		envelope.setAttribute('xmlns:ns','urn:%s' % res_dict['servicename'])
		doc.appendChild(envelope)
		body_elem = doc.createElement('SOAP-ENV:Body')
		body_elem.setAttribute('SOAP-ENV:encodingStyle','http://schemas.xmlsoap.org/soap/encoding/')
		envelope.appendChild(body_elem)
		method_elem = doc.createElement("ns:%sResponse" % res_dict['method'])
		SOAPResponseHandler.value_to_soapxml(res_dict['result'],method_elem,doc,is_toplevel=True)
		body_elem.appendChild(method_elem)
		return doc.toxml(encoding=encoding)

class SOAPFaultHandler(BaseFaultHandler):
	
	_content_type = 'text/xml'
	_stringify_res_dict = True
	soapfault_template = """<?xml version='1.0' encoding='UTF-8'?>
<SOAP-ENV:Envelope
xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/1999/XMLSchema">
	<SOAP-ENV:Body>
		<SOAP-ENV:Fault>
			<faultcode xsi:type="xsd:string"></faultcode>
			<faultstring xsi:type="xsd:string"></faultstring>
			<detail></detail>
		</SOAP-ENV:Fault>
	</SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

	def build_fault_response(self,service_exc,sinfo,methodname,encoding,reflection):
		import xml.dom.minidom as md
		if service_exc.detail:
			detail = service_exc.detail
		else:
			detail = traceback.format_exc()
		d = md.parseString(self.soapfault_template)
		# Extract fault DOM elements
		faultcode_elem = d.getElementsByTagName('faultcode')[0]
		faultstring_elem = d.getElementsByTagName('faultstring')[0]
		detail_elem = d.getElementsByTagName('detail')[0]
		# Set the fault values
		faultcode_elem.appendChild(d.createTextNode(service_exc.faultcode))
		faultstring_elem.appendChild(d.createTextNode(service_exc.faultstring))
		detail_elem.appendChild(d.createTextNode(detail))
		# Return the SoapFault XML object
		return d.toxml(encoding=encoding)

@expose
class SOAPInterface(BaseInterface):

	def __init__(self,sinfo,**kw):
		def_kw = {
			'service_descriptor': SOAPServiceDescriptor,
			'request_handler': SOAPRequestHandler,
			'response_handler': SOAPResponseHandler,
			'fault_handler': SOAPFaultHandler}
		def_kw.update(kw)
		BaseInterface.__init__(self,sinfo,**def_kw)

	@staticmethod
	def _interface_name():
		return 'soap'

	@staticmethod
	def _accept_basetype(typ):
		return pytype_support.count(typ)>0

	@staticmethod
	def _accept_list():
		return True

	@staticmethod
	def _accept_dict():
		return False


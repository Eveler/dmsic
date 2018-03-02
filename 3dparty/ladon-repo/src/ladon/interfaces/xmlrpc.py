# -*- coding: utf-8 -*-

"""XMLRPC-Interface for ladon.
"""

__author__ = 'Dennis Ploeger <develop@dieploegers.de>'

import sys
if sys.version_info[0]==2:
	from StringIO import StringIO
elif sys.version_info[0]>=3:
	from io import StringIO

import base64
import re
import datetime
import traceback
from ladon.exceptions.dispatcher import UndefinedServiceMethod
from ladon.exceptions.service import ClientFault

from ladon.interfaces import expose

from ladon.interfaces.base import BaseInterface, \
    ServiceDescriptor, BaseRequestHandler, BaseResponseHandler, BaseFaultHandler
from ladon.compat import pytype_support, BytesIO, PORTABLE_STRING

from xml.dom import Node

from xml.dom.minidom import parseString, getDOMImplementation

def u(instring):
    if sys.version_info[0]==2:
        return PORTABLE_STRING(instring, 'utf-8')
    else:
        return PORTABLE_STRING(instring)

def is_binary(test_string):
    """Return true if the given filename is binary.
    @attention: based on http://bytes
    .com/topic/python/answers/21222-determine-file-type-binary-text on 6/08/2010
    @author: Trent Mick <TrentM@ActiveState.com>
    @author: Jorge Orpinel <jorge@orpinel.com>"""
    fin = StringIO(test_string)
    try:
        CHUNKSIZE = 1024
        while 1:
            chunk = fin.read(CHUNKSIZE)
            if '\0' in chunk: # found null byte
                return True
            if len(chunk) < CHUNKSIZE:
                break # done
    finally:
        fin.close()

    return False

class XMLRPCServiceDescriptor(ServiceDescriptor):
    """Generate XRDL (based on
        http://code.google.com/p/xrdl/source/browse/documentation/xrdl.xsd)"""

    _content_type = 'text/xml'
    _special_types = []

    def _get_type_name(self, type_class):

        try:

            return type_class.__name__

        except:

            return type(type_class).__name__

    def _type_to_xmlrpc(self, type_name):

        if type_name in ['str', 'unicode']:

            return 'string'

        elif type_name in ['int', 'long']:

            return 'int'

        elif type_name in ['float']:

            return 'double'

        elif type_name == 'datetime.time':

            return 'dateTime8601'

        elif type_name == 'bool':

            return 'boolean'

        elif type_name in self._special_types:

            return type_name

        elif type_name in ['list', 'tuple', 'set']:

            return 'array'

        elif type_name == 'dict':

            return 'struct'

        else:

            # Assume binary if no other type matches

            return 'base64'

    def generate(
        self,
        servicename,
        servicenumber,
        typemanager,
        methodlist,
        service_url,
        encoding
    ):

        type_dict = typemanager.type_dict

        for type_class in type_dict:

            self._special_types.append(self._get_type_name(type_class))

        impl = getDOMImplementation()

        resp_doc = impl.createDocument(None, 'service', None)

        resp_doc.documentElement.setAttribute(
            'url',
            service_url
        )

        resp_doc.documentElement.setAttribute(
            'ns',
            ''
        )

        resp_doc.documentElement.setAttribute(
            'name',
            servicename
        )

        # Types

        types_el = resp_doc.createElement('types')

        for type_class, type_info in type_dict.iteritems():
            type_el = resp_doc.createElement('type')

            type_el.setAttribute('name', type_info['name'])

            for member in type_info['attributes']:

                (member_name, member_type, member_opt) = member

                member_el = resp_doc.createElement('member')

                member_el.setAttribute(
                    'type',
                    self._type_to_xmlrpc(
                        self._get_type_name(member_type)
                    )
                )

                member_el.appendChild(
                    resp_doc.createTextNode(member_name)
                )

                type_el.appendChild(member_el)

            types_el.appendChild(type_el)

        resp_doc.documentElement.appendChild(types_el)

        # Methods

        methods_el = resp_doc.createElement('methods')

        for method in methodlist:

            method_info = method.serialize()

            method_el = resp_doc.createElement('method')

            method_el.setAttribute('name', method.name())
            method_el.setAttribute(
                'result',
                self._type_to_xmlrpc(
                    self._get_type_name(method_info['rtype'][0])
                )
            )

            for param in method.args():

                param_el = resp_doc.createElement('param')

                param_el.setAttribute(
                    'type',
                    self._type_to_xmlrpc(
                        self._get_type_name(param['type'])
                    )
                )

                param_el.appendChild(
                    resp_doc.createTextNode(param['name'])
                )

                method_el.appendChild(param_el)

            methods_el.appendChild(method_el)

        resp_doc.documentElement.appendChild(methods_el)

        return resp_doc.toxml(encoding = encoding)

class XMLRPCRequestHandler(BaseRequestHandler):

    def get_param_value(self, node):
        """Turn a param node into a value
        """

        type_defined = False

        for node_index in range(0, node.childNodes.length):

            if node.childNodes.item(node_index).nodeType != Node.TEXT_NODE:
                type_defined = True

                type_node = node.childNodes.item(node_index)

                current_type = type_node.tagName

        if not type_defined:
            # No type give, assume String

            current_type = "string"

        if current_type in ['i4', 'int']:
            return int(type_node.firstChild.data.strip())
        elif current_type == 'boolean':
            return int(type_node.firstChild.data.strip()) == 1
        elif current_type == 'double':
            return float(type_node.firstChild.data.strip())
        elif current_type in ['dateTime.iso8601', 'base64', 'string']:
            return type_node.firstChild.data.strip()

        # We have a list data type

        if current_type == 'struct':
            return_dict = {}

            members = type_node.getElementsByTagName('member')

            for member_index in range(0, members.length):

                current_member = members.item(member_index)

                name_node = current_member.getElementsByTagName('name')

                if name_node.length > 1:
                    raise ClientFault('More than one name nodes in a struct')

                if name_node.firstChild.nodeType != Node.TEXT_NODE:
                    raise ClientFault(
                        'Unexpected Node type %d while parsing '
                        'a struct member name' %
                            name_node.firstChild.nodeType
                    )

                key = name_node.firstChild.data.strip()

                value_node = current_member.getElementsByTagName('value')

                value = self.get_param_value(value_node)

                return_dict[key] = value

            return return_dict

        if current_type == 'array':

            return_list = []

            values = type_node.getElementsByTagName('value')

            for value_index in range(0, values.length):

                return_list.append(
                    self.get_param_value(values.item(value_index))
                )

            return return_list

    def parse_request(self,req,sinfo,encoding):

        req_dict = {'args': {}}

        req_doc = parseString(req)

        # Find method name

        method_name = req_doc.getElementsByTagName('methodName')

        req_dict['methodname'] = method_name.item(0).firstChild.data.strip()

        # Fill params

        if sinfo.method(req_dict['methodname']) is None:

            # Unknown method

            raise UndefinedServiceMethod(
                'xmlrpc',
                sinfo.servicename,
                'Unknown method %s' % req_dict['methodname']
            )

        args = sinfo.method(req_dict['methodname']).args()

        params = req_doc.getElementsByTagName('param')

        for current_param in range(0, params.length):

            node = params.item(current_param)

            value_node = node.getElementsByTagName('value').item(0)

            value = self.get_param_value(value_node)

            current_arg = args[current_param]

            req_dict['args'][current_arg['name']] = value

        return req_dict

class XMLRPCResponseHandler(BaseResponseHandler):

    _content_type = 'text/xml'
    _stringify_res_dict = False
    datetime_re = None

    def get_xml_value(self, value, resp_doc):

        value_el = resp_doc.createElement('value')

        if isinstance(value, (str, unicode)):

            # Check for special cases base64, dateTime.iso8601

            if is_binary(value):

                base64_el = resp_doc.createElement('base64')
                base64_el.appendChild(
                    resp_doc.createTextNode(base64.b64encode(str(value)))
                )

                value_el.appendChild(base64_el)

            elif self.datetime_re.match(value):

                datetime_el = resp_doc.createElement('dateTime.iso8601')
                datetime_el.appendChild(
                    resp_doc.createTextNode(value)
                )

                value_el.appendChild(datetime_el)

            elif isinstance(value, unicode):

                string_el = resp_doc.createElement('string')
                string_el.appendChild(
                    resp_doc.createTextNode(value)
                )

                value_el.appendChild(string_el)

            else:

                string_el = resp_doc.createElement('string')
                string_el.appendChild(
                    resp_doc.createTextNode(u(value))
                )

                value_el.appendChild(string_el)

        elif isinstance(value, int):

            int_el = resp_doc.createElement('int')
            int_el.appendChild(
                resp_doc.createTextNode(value)
            )

            value_el.appendChild(int_el)

        elif isinstance(value, float):

            double_el = resp_doc.createElement('double')
            double_el.appendChild(
                resp_doc.createTextNode(value)
            )

            value_el.appendChild(double_el)

        elif isinstance(value, bool):

            if value:
                value = 1
            else:
                value = 0

            boolean_el = resp_doc.createElement('boolean')
            boolean_el.appendChild(
                resp_doc.createTextNode(value)
            )

            value_el.appendChild(boolean_el)

        elif isinstance(value, datetime.time):

            datetime_el = resp_doc.createElement('dateTime.iso8601')
            datetime_el.appendChild(
                resp_doc.createTextNode(
                    value.strftime('%Y%m%dT%H:%M:%S')
                )
            )

            value_el.appendChild(datetime_el)

        elif isinstance(value, dict):

            struct_el = resp_doc.createElement('struct')

            for current_member in range(0, len(value.keys())):

                member_key = value.keys()[current_member]

                member_value_el = self.get_xml_value(
                    value[member_key],
                    resp_doc
                )

                member_el = resp_doc.createElement('member')

                name_el = resp_doc.createElement('name')
                name_el.appendChild(
                    resp_doc.createTextNode(member_key)
                )

                member_el.appendChild(name_el)
                member_el.appendChild(member_value_el)

                struct_el.appendChild(member_el)

            value_el.appendChild(struct_el)

        elif isinstance(value, list):

            array_el = resp_doc.createElement('array')
            data_el = resp_doc.createElement('data')

            for current_value in range(0, len(value)):
                data_value_el = self.get_xml_value(
                    value[current_value],
                    resp_doc
                )

                data_el.appendChild(data_value_el)

            array_el.appendChild(data_el)

            value_el.appendChild(array_el)

        return value_el

    def build_response(self,res_dict,sinfo,encoding):
        self.datetime_re = re.compile('\d{8}T\d{2}:\d{2}:\d{2}')

        value = res_dict['result']

        impl = getDOMImplementation()

        resp_doc = impl.createDocument(None, 'methodResponse', None)
        params_el = resp_doc.createElement('params')
        param_el = resp_doc.createElement('param')

        value_el = self.get_xml_value(value, resp_doc)

        param_el.appendChild(value_el)

        params_el.appendChild(param_el)

        resp_doc.documentElement.appendChild(params_el)

        return resp_doc.toxml(encoding = encoding)

class XMLRPCFaultHandler(BaseFaultHandler):
    _content_type = 'text/xml'
    _stringify_res_dict = False

    def build_fault_response(self,service_exc,sinfo,methodname,encoding,reflection):
        if service_exc.detail:
            detail = service_exc.detail
        else:
            detail = traceback.format_exc()
        if service_exc.hint:
            detail += "\n" + service_exc.hint

        detail = detail.replace('\r\n','\n')

        impl = getDOMImplementation()

        resp_doc = impl.createDocument(None, 'methodResponse', None)

        fault_el = resp_doc.createElement('fault')
        value_el = resp_doc.createElement('value')
        struct_el = resp_doc.createElement('struct')

        # Fault-Code

        code_member_el = resp_doc.createElement('member')

        code_name_el = resp_doc.createElement('name')
        code_name_el.appendChild(
            resp_doc.createTextNode('faultCode')
        )

        code_member_el.appendChild(code_name_el)

        code_value_el = resp_doc.createElement('value')

        code_value_int_el = resp_doc.createElement('int')
        code_value_int_el.appendChild(
            resp_doc.createTextNode('99')
        )

        code_value_el.appendChild(code_value_int_el)

        code_member_el.appendChild(code_value_el)

        struct_el.appendChild(code_member_el)

        # Fault-String

        string_member_el = resp_doc.createElement('member')

        string_name_el = resp_doc.createElement('name')
        string_name_el.appendChild(
            resp_doc.createTextNode('faultString')
        )

        string_member_el.appendChild(string_name_el)

        string_value_el = resp_doc.createElement('value')

        string_value_string_el = resp_doc.createElement('string')
        string_value_string_el.appendChild(
            resp_doc.createTextNode(service_exc.faultstring + "\n" + detail)
        )

        string_value_el.appendChild(string_value_string_el)

        string_member_el.appendChild(string_value_el)

        struct_el.appendChild(string_member_el)

        value_el.appendChild(struct_el)
        fault_el.appendChild(value_el)

        resp_doc.documentElement.appendChild(fault_el)

        return resp_doc.toxml(encoding = encoding)

@expose
class XMLRPCInterface(BaseInterface):

    def __init__(self,sinfo,**kw):
        def_kw = {
        'service_descriptor': XMLRPCServiceDescriptor,
        'request_handler': XMLRPCRequestHandler,
        'response_handler': XMLRPCResponseHandler,
        'fault_handler': XMLRPCFaultHandler}
        def_kw.update(kw)
        BaseInterface.__init__(self,sinfo,**def_kw)

    @staticmethod
    def _interface_name():
        return 'xmlrpc'

    @staticmethod
    def _accept_basetype(typ):
        return pytype_support.count(typ)>0

    @staticmethod
    def _accept_list():
        return True

    @staticmethod
    def _accept_dict():
        return True
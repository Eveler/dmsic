import inspect,copy
from ladon.exceptions.types import *
from ladon.types.ladontype import LadonType
from ladon.types.attachment import attachment
from ladon.compat import PORTABLE_STRING_TYPES

def get_userdef_class_attributes(cls,exclude_methods=True):
	base_attrs = dir(type('dummy', (object,), {}))
	this_cls_attrs = dir(cls)
	res = []
	for attr in this_cls_attrs:
		# attr == '__qualname__'
		# Python 3.3 __qualname__ (PEP 3155 -- Qualified name for classes and functions) fix
		if base_attrs.count(attr) or (exclude_methods and inspect.isroutine(getattr(cls,attr)) ) or attr == '__qualname__':
			continue
		res += [attr]
	return res


class TypeManager(object):

	"""
	This class is used by LadonServiceInfo to collect all types that a given
	service depends on. It also keeps track of the parse order so it is possible
	to create service type descriptors in the right order. This will prevent that
	an array of some type is not defined before the type itself.
	
		type_dict: holds all the parsed class-types that are derived from LadonType
		type_order: holds all parsed types in the correct parse order
		primitive_list: A list of all the primitive types a service depends on
	
	Primitive types are defined as all classes that don't inherit LadonType
	"""
	
	global_type_dict = {}
	
	def __init__(self):
		self.type_dict = {}
		self.type_order = []
		self.primitive_list = []
		self.has_lists = False
		self.has_dicts = False
		self.type_parse_order = 0

	
	def add_primitive_type(self,prim):
		if not self.primitive_list.count(prim):
			self.primitive_list += [prim]
	
	def analyze_class(self,cls):
		try:
			inspect.getmro(cls).count(LadonType)
		except Exception as e:
			raise NeedToDefineParseTimeException("class not LadonType inherited - %s" % str(e))
		type_key = cls
		if not type_key in self.type_dict:
			self.type_dict[type_key] = {
				'module': cls.__module__,
				'name': cls.__name__,
				'attributes': [] }
		else:
			return self.type_dict[type_key]
		type_container = self.type_dict[type_key]
		class_attrs = get_userdef_class_attributes(cls)
		for attr in class_attrs:
			attr_val = getattr(cls,attr)
			array_attr = False
			attr_props = {}
			if type(attr_val)==list and len(attr_val)==1:
				attr_val = attr_val[0]
				array_attr = True
				self.has_lists = True
			elif type(attr_val)==dict:
				# Dictionary type definitions for LadonTypes
				# New feature in Ladon 0.6.6
				try:
					temp_attr_val = attr_val['type']
				except AttributeError:
					raise NeedToDefineParseTimeException('Dictionary type definitions must contain the "type" key.\nclass: %s\nattr: %s' % (cls.__name__,attr))
				ok_default_types = []
				if 'nullable' in attr_val:
					if type(attr_val['nullable'])!=bool:
						raise NeedToDefineParseTimeException('Dictionary type definition nullable must be a boolean value.\nclass: %s\nattr: %s' % (cls.__name__,attr))
					attr_props['nullable'] = attr_val['nullable']
					if attr_props['nullable']:
						ok_default_types += [type(None)]
						
				if 'doc' in attr_val:
					temp_doc = attr_val['doc']
					if type(temp_doc) in PORTABLE_STRING_TYPES:
						attr_props['doc'] = [temp_doc]
					elif type(temp_doc)==list:
						attr_props['doc'] = []
						for doc_line in temp_doc:
							if type(doc_line) in PORTABLE_STRING_TYPES:
								attr_props['doc'] += [doc_line]
								
				if 'default' in attr_val:
					ok_default_types += [temp_attr_val]
					if type(attr_val['default']) not in ok_default_types:
						raise NeedToDefineParseTimeException('Default value does not match the attribute type.\nclass: %s\nattr: %s' % (cls.__name__,attr))
					attr_props['default'] = attr_val['default']
					has_default = True
					
				if 'filters' in attr_val:
					filters = attr_val['filters']
					for filter_type in ['incoming_raw','incoming','outgoing','outgoing_raw']:
						if filter_type in filters and hasattr(filters[filter_type],'__iter__') and len(filters[filter_type]):
							# Add attribute filter functions
							if 'filters' not in attr_props:
								attr_props['filters'] = {}
							attr_props['filters'][filter_type] = list(attr_val['filters'][filter_type])
							
				attr_val = temp_attr_val
			elif type(attr_val)!=type:
				raise NeedToDefineParseTimeException("class attributes on LadonTypes must be defined as types, lists.\nclass: %s\nattr: %s" % (cls.__name__,attr))
			if inspect.getmro(attr_val).count(LadonType):
				self.analyze_class(attr_val)
			else:
				self.add_primitive_type(attr_val)
				if attr_val==attachment:
					self.temp_require_multipart = True

			if array_attr:
				if not self.type_order.count([attr_val]):
					self.type_order += [[attr_val]]
				attr_val = [attr_val]
			attr_props['type'] = attr_val
			type_container['attributes'] += [(attr,attr_val,attr_props)]
		if not type_key in self.global_type_dict:
			self.global_type_dict[type_key] = copy.deepcopy(type_container)
		type_container['parse_order'] = self.type_parse_order
		self.type_order += [type_container]
		self.type_parse_order += 1
		return type_container

	def analyze_param(self,param):
		self.temp_require_multipart = False
		if [list,tuple].count(type(param)):
			# Parameter seems to be an array
			if len(param)!=1:
				raise NeedToDefineParseTimeException("Only one element is allowed when defining ladon arrays")
			if type(param[0])!=type:
				raise NeedToDefineParseTimeException("Only types are allowed as list-element when defining an array")
			
			if inspect.getmro(param[0]).count(LadonType):
				self.analyze_class(param[0])
			else:
				self.add_primitive_type(param[0])
				if param[0]==attachment:
					self.temp_require_multipart = True

			self.has_lists = True
			if not self.type_order.count([param[0]]):
				self.type_order += [[param[0]]]
		elif type(param)==type:
			if inspect.getmro(param).count(LadonType):
				self.analyze_class(param)
			else:
				self.add_primitive_type(param)
				if param==attachment:
					self.temp_require_multipart = True
		else:
			raise NeedToDefineParseTimeException("Ladonized param definition must be a LadonType or iterable")
		return self.temp_require_multipart

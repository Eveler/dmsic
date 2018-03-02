# -*- coding: utf-8 -*-

from ladon.exceptions.types import *
from ladon.types import get_type_info
import inspect,sys,re
from ladon.types.attachment import attachment,extract_attachment_reference
from ladon.compat import PORTABLE_BYTES,PORTABLE_STRING

rx_cid = re.compile('^cid:(.+)$',re.I)

class LadonType(object):
	"""LadonType must be specialized by all complex service types. It tells the Ladon
	framework that it should expect multiple primitives and/or lists to be defined as
	class attributes. Using LadonType it is possible to build nested types.

	LadonType specializations must define it's attributes as types (either primitive
	types, other LadonType specialization types, lists of primitive or lists of 
	LadonType specialization). This explains the Ladon framework what to expect. There
	are 5 primitive types:
		
		+------------+------------+
		| Python 2   | Python 3   |
		+============+============+
		| str        | bytes      |
		+------------+------------+
		| unicode    | str        |
		+------------+------------+
		| bool       | bool       |
		+------------+------------+
		| float      | float      |
		+------------+------------+
		| int        | int        |
		+------------+------------+
		| attachment | attachment |
		+------------+------------+
	"""
	
	def __init__(self,prime_dict=None,tc=None,export_dict=None):
		global rx_cid
		if type(prime_dict)==dict:
			type_dict = get_type_info(self.__class__)
			for attr_name,attr_type,props in type_dict['attributes']:
				if type(attr_type)==list:
					# Assumption list attributes are always optional
					attr_val = []
					if attr_name in prime_dict:
						if prime_dict[attr_name]==None:
							# Null lists are accepted ans parsed as empty list
							prime_dict[attr_name] = []
						elif type(prime_dict[attr_name])!=list:
							raise ListAttributeMismatch(
								self,prime_dict,
								'Expected list type for attribute "%s" got "%s"' % \
								(attr_name,str(type(prime_dict[attr_name]))),
								attr_name)
						type_info = get_type_info(attr_type[0])
						try:
							if type_info:
								for item in prime_dict[attr_name]:
									attr_val += [attr_type[0](prime_dict=item,tc=tc,export_dict=export_dict)]
							elif attr_type[0]==attachment:
								for item in prime_dict[attr_name]:
									try:
										attr_val += [extract_attachment_reference(item,export_dict,tc.encoding)]
									except Exception as e:
										raise NonExistingAttachment(
											self,prime_dict,
											str(e),
											attr_name)
							else:
								for item in prime_dict[attr_name]:
									attr_val += [tc.from_unicode_string(item,attr_type[0],attr_name=attr_name)]
						except Exception as e:
							raise SubitemTypeMismatch(
								self,prime_dict,
								'Type mismatch for subitem of attibute "%s", expected "%s" got "%s"\nDetails:%s' % \
								(attr_name,str(attr_type[0]),str(item),str(e)),
								attr_name)
				else:
					filters = props.get('filters')
					# Description of incoming filters:
					# PORTABLE_BYTES = Python 2: str, Python 3: bytes
					# * 'incoming_raw': 
					#     list functions that recieve the raw value (PORTABLE_BYTES). The function can for
					#     instance do business logic validation and raise a client fault if the value makes
					#     no sense.
					#     Or it can return a new value (PORTABLE_BYTES) and thereby acting as a raw modifier.
					# * 'incoming': 
					#     list functions that recieve the value in the service specified type.
					#     The function can do validation raise a client fault if the value makes no sense.
					#     Or it can return a new value in the service specified type acting as a modifier.
					prefilters = None
					postfilters = None
					if filters and filters.get('incoming_raw'):
						prefilters = filters.get('incoming_raw')
					if filters and filters.get('incoming'):
						postfilters = filters.get('incoming')

					# Need some kind of check for optional in type definition class
					if attr_name in prime_dict:
						type_info = get_type_info(attr_type)
						val = prime_dict[attr_name]
						
						if val==None and props.get('nullable')==True:
							attr_val = val
							## Run filters on incoming value if value was None
							#if filters and filters.get('incoming'):
								#for func in filters.get('incoming'):
									#attr_val = func(attr_val)
						elif type_info:
							attr_val = attr_type(prime_dict=val,tc=tc,export_dict=export_dict)
						elif attr_type==attachment:
							try:
								attr_val = extract_attachment_reference(val,export_dict,tc.encoding)
							except Exception as e:
								raise NonExistingAttachment(
									self,prime_dict,
									str(e),
									attr_name)
						else:
							attr_val = tc.from_unicode_string(val,attr_type,prefilters,postfilters,attr_name=attr_name)
					else:
						attr_val=props.get('default')
						if attr_val==None and props.get('nullable')!=True:
							raise MandatoryAttributeMissing(
								self,prime_dict,
								'Missing prime_dict attribute is not nullable "%s"' % attr_name,
								attr_name)
						## Run filters on incoming value if value was None
						#if filters and filters.get('incoming'):
							#for func in filters.get('incoming'):
								#attr_val = func(attr_val)

				setattr(self,attr_name,attr_val)
		elif prime_dict:
			type_dict = TypeManager.global_type_dict[self.__class__]
			raise LadonTypePrimerMismatch(
				self,prime_dict,
				'Dictionary expected for prime_dict got "%s" of value "%s"' % \
				(type(prime_dict),
				str(prime_dict)))
			

	def __dict__(self,tc,response_attachments=None):
		"""
		Convert LadonType to dict representation. Argument tc is a TypeConverter
		which holds information about string conversions and whether unsafe conversions
		are allowed or not.
		"""
		
		res_dict = {}
		type_dict = TypeManager.global_type_dict[self.__class__]
		for attr_name,attr_type,props in type_dict['attributes']:
			if type(attr_type)==list:
				# Assumption list attributes are always optional
				try:
					attr_val = getattr(self,attr_name)
				except:
					# assumed optional, so this is ok
					continue
				if not type(attr_val)==list:
					raise ListExpected(
						self,
						'Expected list got: %s' % type(attr_val),
						attr_name)
				if attr_type == attr_val:
					# attribute not touched and still exposing the type
					continue
				
				attr_list = []
				res_dict[attr_name] = attr_list
				
				is_ladontype_items = False
				if attr_type[0] in TypeManager.global_type_dict:
					is_ladontype_items = True
				
				for val in attr_val:
					if is_ladontype_items:
						attr_list += [val.__dict__(tc,response_attachments)]
					elif attr_type[0] == attachment:
						if not type(val) == attachment:
							raise AttachmentExpected(
								self,
								'Expected list of attachments got item of type: %s' % type(val),
								attr_name)
						attr_list += [response_attachments.add_attachment(val)]
					else:
						attr_list += [tc.to_unicode_string(val,attr_type[0],attr_name=attr_name)]
			else:
				try:
					attr_val = getattr(self,attr_name)
				except:
					if props.get('nullable')==True:
						attr_val = props.get('default')
					else:
						# Assumption non-list non nullable attributes are not optional
						raise NeedToDefineParseTimeException('Non-optional attribute missing in LadonType while serializing')

				filters = props.get('filters')
				# Description of outgoing filters:
				# PORTABLE_STRING = Python 2: unicode, Python 3: str
				# * 'outgoing': 
				#     list functions that recieve the value in the service specified type.
				#     The function can do validation raise a server fault if the value makes no sense.
				#     Or it can return a new value in the service specified type acting as a modifier.
				# * 'outgoing_raw': 
				#     list functions that recieve the raw value (PORTABLE_STRING). The function can for
				#     instance do business logic validation and raise a server fault if the value makes
				#     no sense.
				#     Or it can return a new value (PORTABLE_STRING) and thereby acting as a raw modifier.
				prefilters = None
				postfilters = None
				if filters and filters.get('outgoing'):
					prefilters = filters.get('outgoing')
				if filters and filters.get('outgoing_raw'):
					postfilters = filters.get('outgoing_raw')

				if attr_val==None:
					# Attribute is None, this is OK if the attribute is
					# nullable.
					if props.get('nullable')==True:
						res_dict[attr_name] = attr_val
					else:
						# Attribute is not nullable
						raise NeedToDefineParseTimeException('Attribute "%s" (class: "%s") is not nullable' % (attr_name,(self.__class__)))
				elif isinstance(attr_val,dict) and props.get('type')==attr_type:
					# Attribute is dictionary type defined and untouched set default value
					# if available.
					attr_val = props.get('default')
					if attr_val==None and props.get('nullable')!=True:
						# Attribute is not nullable
						raise NeedToDefineParseTimeException('Attribute "%s" (class: "%s") is not nullable' % (attr_name,(self.__class__)))
					res_dict[attr_name] = attr_val
				elif attr_type in TypeManager.global_type_dict:
					try:
						res_dict[attr_name] = attr_val.__dict__(tc,response_attachments)
					except Exception as e:
						raise AttributeConversionException(
							self,
							'An exception was raised while processing LadonType attribute "%s"\nDetails:%s' % (attr_name,str(e)),
							attr_name)
				elif attr_type == attachment:
					if not type(attr_val) == attachment:
						raise AttachmentExpected(
							self,
							'Expected attachment got %s' % type(attr_val),
							attr_name)
					res_dict[attr_name] = response_attachments.add_attachment(attr_val)
				else:
					try:
						res_dict[attr_name] = tc.to_unicode_string(attr_val,attr_type,prefilters,postfilters,attr_name=attr_name)
					except Exception as e:
						raise AttributeConversionException(
							self,
							'An exception was raised while processing attribute "%s"\nDetails:%s' % (attr_name,str(e)),
							attr_name)
		return res_dict

from ladon.types.typemanager import TypeManager

# -*- coding: utf-8 -*-
import sys
from ladon.exceptions.types import *
from ladon.compat import PORTABLE_BYTES,PORTABLE_STRING,pytype_support,safe_conversions

class TypeConverter(object):
	
	"""The type converter mainly serves as a tool for the dispatcher providing the means to
	validate and convert between the interface and function layers
	"""
	
	def __init__(self,encoding='UTF-8',allow_unsafe_conversion=False,only_strings_to_unicode=True):
		"""In the TypeConverter constructor you can set conversion properties like which
		encoding to use when converting forth and back between unicode to str (or bytes and
		str for python 3). The default encoding is UTF-8.
		allow_unsafe_conversion is a boolean that tells the TypeConverter if unsafe conversions are allowed,
		An example of an unsafe conversion is float to int, as any floating point part will be truncated
		in the conversion.
		only_strings_to_unicode tells the converter to let types other than unicode and str (or bytes and
		str in python 3) be converted to the expected type when calling to_unicode_string
		"""
		# Converter options
		self.encoding=encoding
		self.allow_unsafe_conversion = allow_unsafe_conversion
		self.only_strings_to_unicode = only_strings_to_unicode

	def from_unicode_string(self,val,typ,prefilters=None,postfilters=None,attr_name=None):
		"""Convert a unicode string to certain types.
		"""
		# Run incoming_raw filters aka. incoming prefilters
		if prefilters:
			for func in prefilters:
				val = func(val)
		
		vtyp = type(val)
		
		# The following fix (accepting booleans) has been added because
		# keyword parameter parse_constant of json.loads has changed to
		# not react on true/false (http://bugs.python.org/issue14692)
		if vtyp==bool and typ==bool:
			val = PORTABLE_STRING(val)
			vtyp = PORTABLE_STRING
		
		# Check the value type
		if not vtyp==PORTABLE_STRING:
			raise NonUnicodeError(type(val),attr_name=attr_name)
		
		# unicode to unicode or raw string
		if typ in [PORTABLE_BYTES,PORTABLE_STRING]:
			if typ==PORTABLE_BYTES:
				val = val.encode(self.encoding)
			# Run incoming filters aka. incoming postfilters
			if postfilters:
				for func in postfilters:
					val = func(val)
			return val
		
		# other primitive types
		try:
			if typ==bool and (val[0].upper()==PORTABLE_STRING('F') or val.strip()=='0'):
				val = False
			else:
				val = typ(val)
			# Run incoming filters aka. incoming postfilters
			if postfilters:
				for func in postfilters:
					val = func(val)
			return val
		except Exception as e:
			raise FromUnicodeConversionError(typ,str(e),attr_name=attr_name)


	def to_unicode_string(self,val,expected_typ,prefilters=None,postfilters=None,attr_name=None):
		"""Convert a primitive type to unicode. The method uses TypeConverter
		options in the decition making, and encoding.
		"""
		# Run outgoing filters aka. outgoing prefilters
		if prefilters:
			for func in prefilters:
				val = func(val)
		typ = type(val)
		# Expecting unicode or raw string
		if expected_typ in [PORTABLE_BYTES,PORTABLE_STRING]:
			# No unsafe conversion can enter here as long as the user's service method obeys
			# the internal encoding it advertises for raw strings (aka bytes in python 3)
			if typ==PORTABLE_STRING:
				pass
			elif typ==PORTABLE_BYTES:
				val = PORTABLE_STRING(val,self.encoding)
			else:
				val = PORTABLE_STRING(val)
			# Run outgoing_raw filters aka. outgoing postfilters
			if postfilters:
				for func in postfilters:
					val = func(val)
			return val
		
		if not self.allow_unsafe_conversion:
			# Check if the conversion is unsafe
			if expected_typ not in safe_conversions[typ]:
				raise UnsafeConversionDisabled(typ,expected_typ,attr_name=attr_name)
		try:
			val = expected_typ(val)
		except Exception as e:
			raise UnsafeConversionError(typ,expected_typ,str(e),attr_name=attr_name)
		if self.only_strings_to_unicode:
			pass
		else:
			if expected_typ==bool:
				val = PORTABLE_STRING(val).lower()
			val = PORTABLE_STRING(val)
		# Run outgoing_raw filters aka. outgoing postfilters
		if postfilters:
			for func in postfilters:
				val = func(val)
		return val

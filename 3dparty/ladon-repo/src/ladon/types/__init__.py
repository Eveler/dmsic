# -*- coding: utf-8 -*-

def validate_type(typ,val):
	if [tuple,list].count(type(typ)):
		if not [tuple,list].count(type(val)):
			return False
		for i in val:
			if type(i)!=typ[0]:
				return False
	else:
		if typ!=type(val):
			return False
	return True

def get_type_info(typ):
	"""
	Convert a type to ladon type dict. If the type is a LadonType and contained in the service being processed
	the type dict will be returned, otherwise None is returned.
	"""
	from ladon.types.typemanager import TypeManager
	if not [list,tuple].count(type(typ)) and typ in TypeManager.global_type_dict:
		return TypeManager.global_type_dict[typ]
	else:
		return None

def expand_value(value,valtype, encoding='UTF-8',allow_unsafe_conversion=False,only_strings_to_unicode=True,service_name='unknown', method_name='unknown'):
	"""
	Convert the result of a method call to it's dictionary representation.
	"""
	from ladon.types.typeconverter import TypeConverter
	from ladon.tools.multiparthandler import AttachmentHandler
	from ladon.exceptions.types import AttachmentExpected
	response_attachments = AttachmentHandler()
	tc = TypeConverter(encoding=encoding,allow_unsafe_conversion=allow_unsafe_conversion,only_strings_to_unicode=only_strings_to_unicode)
	type_info = get_type_info(valtype)
	if type_info==None:
		if [list,tuple].count(type(valtype)):
			ret = []
			type_info = get_type_info(valtype[0])
			if value == valtype:
				# Assumption list attributes are always optional
				return
			
			if type_info:
				for item in value:
					ret += [item.__dict__(tc,response_attachments)]
			elif valtype[0]==attachment:
				for item in value:
					if not type(item) == attachment:
						raise AttachmentExpected(service_name,method_name,'Attachment expected got: %s' % type(item))
					ret += [response_attachments.add_attachment(item)]
			else:
				for item in value:
					ret += [tc.to_unicode_string(item,valtype[0])]
		elif valtype==attachment:
			ret = response_attachments.add_attachment(value)
		else:
			ret = tc.to_unicode_string(value,valtype)
	else:
		ret = value.__dict__(tc,response_attachments)
	
	return ret


def result_to_dict(method_info,result, encoding='UTF-8',allow_unsafe_conversion=False,only_strings_to_unicode=True):
	"""
	Convert the result of a method call to it's dictionary representation.
	"""
	from ladon.types.typeconverter import TypeConverter
	from ladon.tools.multiparthandler import AttachmentHandler
	from ladon.exceptions.types import AttachmentExpected
	response_attachments = AttachmentHandler()
	tc = TypeConverter(encoding=encoding,allow_unsafe_conversion=allow_unsafe_conversion,only_strings_to_unicode=only_strings_to_unicode)
	if method_info==None:
		res_dict = {}
		typ = type(result)
		servicename = 'None'
	else:
		res_dict = {
			'servicename': method_info.sinfo.servicename,
			'servicenumber': method_info.sinfo.servicenumber,
			'method': method_info.name()}
		typ = method_info._rtype
		servicename = method_info.sinfo.servicename
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
						raise AttachmentExpected('unknown',servicename,'Attachment expected got: %s' % type(item))
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
	
	return res_dict

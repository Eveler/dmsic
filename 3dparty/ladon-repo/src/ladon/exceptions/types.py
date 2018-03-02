from ladon.exceptions.base import LadonException

class LadonTypeException(LadonException):
	def __init__(self,text):
		LadonException.__init__(self)
		self.text = text
		
	def __str__(self):
		return self.text


class LadonTypePrimingException(LadonTypeException):
	def __init__(self,ladon_inst,prime_dict,text,attr_name=None):
		LadonTypeException.__init__(self,text)
		self.ladon_inst = ladon_inst
		self.prime_dict = prime_dict
		self.attr_name = attr_name
		
	def classname(self):
		return str(self.ladon_inst.__class__)
		
	def __str__(self):
		exc_info = ['classname: %s' % self.classname()]
		if self.attr_name:
			exc_info += ['attribute: %s' % self.attr_name]
		return "\n%s\n%s" % ("\n".join(exc_info),self.text)


class LadonTypeToDictException(LadonTypeException):
	def __init__(self,ladon_inst,text,attr_name=None):
		LadonTypeException.__init__(self,text)
		self.ladon_inst = ladon_inst
		self.attr_name = attr_name
		
	def classname(self):
		return str(self.ladon_inst.__class__)
		
	def __str__(self):
		exc_info = ['classname: %s' % self.classname()]
		if self.attr_name:
			exc_info += ['attribute: %s' % self.attr_name]
		return "\n%s\n%s" % ("\n".join(exc_info),self.text)


class ListAttributeMismatch(LadonTypePrimingException):
	def __init__(self,ladon_inst,prime_dict,text,attr_name=None):
		LadonTypePrimingException.__init__(self,ladon_inst,prime_dict,text,attr_name)
	

class SubitemTypeMismatch(LadonTypePrimingException):
	def __init__(self,ladon_inst,prime_dict,text,attr_name=None):
		LadonTypePrimingException.__init__(self,ladon_inst,prime_dict,text,attr_name)
	

class MandatoryAttributeMissing(LadonTypePrimingException):
	def __init__(self,ladon_inst,prime_dict,text,attr_name=None):
		LadonTypePrimingException.__init__(self,ladon_inst,prime_dict,text,attr_name)

class NonExistingAttachment(LadonTypePrimingException):
	def __init__(self,ladon_inst,prime_dict,text,attr_name=None):
		LadonTypePrimingException.__init__(self,ladon_inst,prime_dict,text,attr_name)

class LadonTypePrimerMismatch(LadonTypePrimingException):
	def __init__(self,ladon_inst,prime_dict,text,attr_name=None):
		LadonTypePrimingException.__init__(self,ladon_inst,prime_dict,text,attr_name)
	

class NeedToDefineParseTimeException(LadonTypeException):
	def __init__(self,text):
		LadonTypeException.__init__(self,text)

class UnsafeConversionDisabled(LadonTypeException):
	def __init__(self,val_type,expected_type,attr_name=None):
		txt = "Unsafe conversions are disabled in the method called service method,\n"
		txt += "but the dispatcher encountered a potential unsafe conversion between types %s and %s.\nWhile handling attribute: %s\n" % (str(val_type),str(expected_type),str(attr_name))
		txt += 'Unsafe conversions can be enabled using the keyword argument "allow_unsafe_conversion" '
		txt += 'in the "ladonize" decorator.'
		LadonTypeException.__init__(self,txt)

class UnsafeConversionError(LadonTypeException):
	def __init__(self,val_type,expected_type,extra_txt,attr_name=None):
		txt = "Conversion failed while doing an unsafe conversion between types %s and %s\nWhile handling attribute: %s" % (str(val_type),str(expected_type),str(attr_name))
		txt += extra_txt
		LadonTypeException.__init__(self,txt)

class NonUnicodeError(LadonTypeException):
	def __init__(self,val_type,attr_name=None):
		txt = "Values must be unicode while converting from string to Ladon supported types: encountered %s\nWhile handling attribute: %s" % (val_type,str(attr_name))
		LadonTypeException.__init__(self,txt)


class FromUnicodeConversionError(LadonTypeException):
	def __init__(self,typ,extra_txt,attr_name=None):
		txt = "Failed to convert from unicode string to Ladon supported type: %s\nWhile handling attribute: %s" % (str(typ),str(attr_name))
		txt += extra_txt
		LadonTypeException.__init__(self,txt)

class ListExpected(LadonTypeToDictException):
	def __init__(self,ladon_inst,text,attr_name=None):
		LadonTypeToDictException.__init__(self,ladon_inst,text,attr_name)

class AttachmentExpected(LadonTypeToDictException):
	def __init__(self,ladon_inst,text,attr_name=None):
		LadonTypeToDictException.__init__(self,ladon_inst,text,attr_name)


class AttributeConversionException(LadonTypeToDictException):
	def __init__(self,ladon_inst,text,attr_name=None):
		LadonTypeToDictException.__init__(self,ladon_inst,text,attr_name)

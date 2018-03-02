from ladon.exceptions.base import LadonException

class LadonizeException(LadonException):
	def __init__(self,sinfo,method):
		LadonException.__init__(self)
		self.sinfo = sinfo
		self.method = method
		
	def longstr(self):
		return 'Method "%s" in service "%s" [%s:%d]' % (self.method,self.sinfo.servicename,self.sinfo.sourcefile,self.sinfo.lineno)
	def shortstr(self):
		return '%s::%s' % (self.sinfo.servicename,self.method)


class ArgDefCountMismatch(LadonizeException):
	"""Exception is raised if the number of argument type defines passed to the ladonize
	decorator does not match the number of arguments that the method takes.
	example:
	
	@ladonize(String,Int,_rtype=String)
	def adduser(username,id,password):
		...
		implementation
		...
		
	In the example above only 2 arguments have been defined in the ladonize decorator, but
	the method takes 3.
	"""
	def __init__(self,sinfo,method,ladonize_argtypes,method_argnames):
		LadonizeException.__init__(self,sinfo,method)
		self.ladonize_argtypes = ladonize_argtypes
		self.method_argnames = method_argnames
	
	def __str__(self):
		return 'Mismatch between the number of argument type defines (%d) and the actual number of arguments in "%s" (%d)' % \
			(len(self.ladonize_argtypes),self.shortstr(),len(self.method_argnames))


class ArgTypeMismatch(LadonizeException):
	"""Exception is raised when a ladonized method is called with arguments that do not
	match the pre-defined argument types.
	"""
	def __init__(self,sinfo,method,argname,expected_type,recieved_type):
		LadonizeException.__init__(self,sinfo,method)
		self.argname = argname
		self.expected_type = expected_type
		self.recieved_type = recieved_type
	
	def __str__(self):
		return 'Type mismatch while passing argument "%s" to %s: Expected %s recieved %s' % \
			(self.argname,self.shortstr(),self.expected_type,self.recieved_type)


class DefaultArgTypeMismatch(LadonizeException):
	"""Exception is raised when a ladonized method has default values that do not
	match the pre-defined argument types.
	"""
	def __init__(self,sinfo,method,argname,expected_type,recieved_type):
		LadonizeException.__init__(self,sinfo,method)
		self.argname = argname
		self.expected_type = expected_type
		self.recieved_type = recieved_type
	
	def __str__(self):
		return 'Default type mismatch on argument "%s" in %s: Expected %s recieved %s' % \
			(self.argname,self.shortstr(),self.expected_type,self.recieved_type)


class ReturnTypeUndefined(LadonizeException):
	"""Exception is raised when a ladonized method is called with arguments that do not
	match the pre-defined argument types.
	"""
	def __init__(self,sinfo,method):
		LadonizeException.__init__(self,sinfo,method)
	
	def __str__(self):
		return 'Ladonized method (%s) must have a return type defined (keyword: "_rtype")' % \
			(self.shortstr())


class ReturnTypeMismatch(LadonizeException):
	"""Exception is raised when a ladonized method is called with arguments that do not
	match the pre-defined argument types.
	"""
	def __init__(self,sinfo,method,expected_rtype,recieved_rtype):
		LadonizeException.__init__(self,sinfo,method)
		self.expected_rtype = expected_rtype
		self.recieved_rtype = recieved_rtype
	
	def __str__(self):
		return 'Return-type mismatch in %s: Expected %s recieved %s' % \
			(self.shortstr(),self.expected_rtype,self.recieved_rtype)


class NeedToDefineException(LadonException):
	def __init__(self,text):
		LadonException.__init__(self)
		self.txt = text
	
	def __str__(self):
		return self.txt

from ladon.exceptions.base import LadonException

class LadonDispatchException(LadonException):
	def __init__(self,text,ifname=None,sname=None):
		LadonException.__init__(self)
		self.text = text
		self.ifname = ifname
		self.sname = sname
		
	def __str__(self):
		if not self.ifname and not self.sname:
			return self.text
		elif not self.sname:
			return "\ninterface name: %s\n%s" % (self.ifname,self.text)
		else:
			return "\ninterface name: %s\nservice name: %s\n%s" % (self.ifname,self.sname,self.text)
			
class UndefinedInterfaceName(LadonDispatchException):
	def __init__(self,ifname,text):
		LadonDispatchException.__init__(self,text,ifname=ifname)


class UndefinedService(LadonDispatchException):
	def __init__(self,ifname,text):
		LadonDispatchException.__init__(self,text,ifname=ifname)


class UndefinedServiceMethod(LadonDispatchException):
	def __init__(self,ifname,sname,text):
		LadonDispatchException.__init__(self,text,ifname=ifname,sname=sname)

class NonExistingAttachment(LadonDispatchException):
	def __init__(self,ifname,sname,text):
		LadonDispatchException.__init__(self,text,ifname=ifname,sname=sname)

class InvalidAttachmentReference(LadonDispatchException):
	def __init__(self,ifname,sname,text):
		LadonDispatchException.__init__(self,text,ifname=ifname,sname=sname)

from ladon.compat import PORTABLE_STRING
from ladon.ladonizer import ladonize
from ladon.types.ladontype import LadonType

class data(LadonType):
	simple = PORTABLE_STRING
	array = [ PORTABLE_STRING ]

class MultiRefService(object):
	
	@ladonize(data,rtype=data)
	def op1(self,p1):
		return p1

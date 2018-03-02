from ladon.types.ladontype import LadonType
from ladon.ladonizer import ladonize
from ladon.compat import PORTABLE_STRING,PORTABLE_BYTES

class Customer(LadonType):
	cid = PORTABLE_BYTES
	name = PORTABLE_STRING

class Report(LadonType):
	rid = PORTABLE_BYTES
	summary = PORTABLE_STRING
	nulllist = [ int ]
	customer = {
		'type': Customer,
		'nullable': True
	}

class CustomerService(object):

	@ladonize(Report,rtype=Report)
	def addReport(self,report):
		return report

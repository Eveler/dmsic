from ladon.ladonizer import ladonize
from ladon.types.ladontype import LadonType

class KeyValue(LadonType):
	key = unicode
	value = unicode



class KVService(object):

	@ladonize([KeyValue], rtype=unicode)
	def testKeyValues(self, keyvalues):
		return unicode(str(keyvalues))



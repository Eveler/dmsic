# -*- coding: utf-8 -*-
from ladon.ladonizer import ladonize
from ladon.compat import PORTABLE_BYTES,PORTABLE_STRING,PORTABLE_STRING_TYPES
# Portable types are defined like this in ladon.compat:
#
#if sys.version_info[0]==2:
	#PORTABLE_BYTES = str
	#PORTABLE_STRING = unicode
	#PORTABLE_STRING_TYPES = [unicode,str]
#elif sys.version_info[0]>=3:
	#PORTABLE_BYTES = bytes
	#PORTABLE_STRING = str
	#PORTABLE_STRING_TYPES = [str,bytes]

class TypeTestService(object):
	
	@ladonize(PORTABLE_BYTES,rtype=PORTABLE_BYTES,encoding='utf-8')
	def conversion(self,in_bytes):
		in_str = in_bytes.decode('utf-8')
		return in_str.encode('utf-8')

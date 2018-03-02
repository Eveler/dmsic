# -*- coding: utf-8 -*-
from ladon.ladonizer import ladonize
from ladon.compat import PORTABLE_BYTES,PORTABLE_STRING,PORTABLE_STRING_TYPES

class CollectionTestService(object):
	
	@ladonize(rtype=PORTABLE_STRING)
	def method_one(self):
		return "one"

	@ladonize(rtype=PORTABLE_STRING)
	def method_two(self):
		return "two"

	@ladonize(rtype=PORTABLE_STRING)
	def method_three(self):
		return "three"

	@ladonize(rtype=PORTABLE_STRING)
	def method_four(self):
		return "four"

	@ladonize(rtype=PORTABLE_STRING)
	def method_five(self):
		return "five"

# -*- coding: utf-8 -*-

from ladon.ladonizer import ladonize
from ladon.compat import PORTABLE_BYTES,PORTABLE_STRING,PORTABLE_STRING_TYPES
import sys
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

class StringTestService(object):
	
	@ladonize(PORTABLE_BYTES,rtype=PORTABLE_BYTES,encoding='latin-1')
	def bytes_in_bytes_out(self,in_string):
		"""
		This test is desigened to take input that consists of characters
		contained in the latin-1 (iso-8859-1) character set. The incomming
		bytes are mirrored back to the client.
		Inside the method we test that the incomming encoding is endeed correct.
		
		@param in_string: The input string that will be mirrored back to the client. 
		"""
		# check type
		if type(in_string) != PORTABLE_BYTES:
			return b'wrong_type'
		# Test that the incomming bytes are correct encoded
		try:
			in_str = in_string.decode('latin-1')
		except:
			return b'wrong_encoding'
		
		if sys.version_info[0]>=3:
			in_str += 'æøåÆØÅß'
		else:
			in_str += PORTABLE_STRING('æøåÆØÅß','utf-8')
		return in_str.encode('latin-1')


	@ladonize(PORTABLE_STRING,rtype=PORTABLE_BYTES,encoding='latin-1')
	def uni_in_bytes_out(self,in_string):
		"""
		This test is desigened to take unicode string input. The incomming
		string is mirrored back to the client as bytes in latin-1 encoding.
		Inside the method we test that the incomming string is unicode.
		
		@param in_string: The input string that will be mirrored back to the client.
		"""
		# check type
		if type(in_string) != PORTABLE_STRING:
			return b'wrong_type'
		
		if sys.version_info[0]>=3:
			in_string += 'æøåÆØÅß'
		else:
			in_string += PORTABLE_STRING('æøåÆØÅß','utf-8')
		return in_string.encode('latin-1')


	@ladonize(PORTABLE_BYTES,rtype=PORTABLE_STRING,encoding='latin-1')
	def bytes_in_uni_out(self,in_string):
		"""
		This test is desigened to take input that consists of characters
		contained in the latin-1 (iso-8859-1) character set. The incomming
		bytes are mirrored back to the client.
		Inside the method we test that the incomming encoding is endeed correct.
		
		@param in_string: The input string that will be mirrored back to the client. 
		"""
		# check type
		if type(in_string) != PORTABLE_BYTES:
			if sys.version_info[0]>=3:
				return 'wrong_type'
			else:
				return PORTABLE_STRING('wrong_type','utf-8')
		# Test that the incomming bytes are correct encoded
		try:
			in_str = in_string.decode('latin-1')
		except:
			if sys.version_info[0]>=3:
				return 'wrong_encoding'
			else:
				return PORTABLE_STRING('wrong_encoding','utf-8')
			
		
		if sys.version_info[0]>=3:
			in_str += 'æøåÆØÅß'
		else:
			in_str += PORTABLE_STRING('æøåÆØÅß','utf-8')
		return in_str


	@ladonize(PORTABLE_STRING,rtype=PORTABLE_STRING)
	def uni_in_uni_out(self,in_string):
		"""
		This test is desigened to take input that consists of characters
		contained in the latin-1 (iso-8859-1) character set. The incomming
		bytes are mirrored back to the client.
		Inside the method we test that the incomming encoding is endeed correct.
		
		@param in_string: The input string that will be mirrored back to the client. 
		"""
		# check type
		if type(in_string) != PORTABLE_STRING:
			if sys.version_info[0]>=3:
				return 'wrong_type'
			else:
				return PORTABLE_STRING('wrong_type','utf-8')
		
		if sys.version_info[0]>=3:
			in_string += 'æøåÆØÅß'
		else:
			in_string += PORTABLE_STRING('æøåÆØÅß','utf-8')
		return in_string

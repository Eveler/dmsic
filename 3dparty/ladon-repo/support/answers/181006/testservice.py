from ladon.ladonizer import ladonize
from ladon.compat import PORTABLE_STRING
from ladon.server.customresponse import CustomResponse
from ladon.exceptions.service import ServerFault, ClientFault

class TestService(object):
	"""
	Search through albums and bands.
	"""

	@ladonize(PORTABLE_STRING,rtype=[ PORTABLE_STRING ])
	def createServerFault(self,search_frase=PORTABLE_STRING('')):
		# A problem occurred on the server-side while invoking a method. Signal
		# this back to the client as a server fault.
		raise ServerFault('Server problem occured while executing method')

	@ladonize(PORTABLE_STRING,rtype=[ PORTABLE_STRING ])
	def blameClientFault(self,search_frase=PORTABLE_STRING('')):
		# In this method I raise a client fault from within a method invokation.
		# This meens that the client sent a request that has the correct signature
		# in regards to methodname and argument types. Instead it could be that the
		# combination of arguments does not make any logical sense. In this type of
		# situation it is sometimes preferred to send a client fault  
		raise ClientFault('Arguments parsed to method makes no sense')

	@ladonize(int,rtype=[ PORTABLE_STRING ])
	def unmanagedFault(self,anumber):
		# In this example I call an unexisting method. The result should be
		# that the dispatcher catches the exception and converts it to a
		# ServerFault
		unexistingMethod()

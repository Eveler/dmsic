from suds.client import Client
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

cli = Client("http://127.0.0.1:8888/TestService/soap/description",cache=None)

print("\n\nServer Fault")
try:
	cli.service.createServerFault()
except Exception as e:
	print e

print("\n\nBlame Client Fault")
try:
	cli.service.blameClientFault()
except Exception as e:
	print e

print("\n\nUnmanaged Fault")
try:
	cli.service.unmanagedFault(1)
except Exception as e:
	print e

print("\n\nUnmanaged Fault - dispatcher-side")
try:
	cli.service.unmanagedFault('fdgerg')
except Exception as e:
	print e





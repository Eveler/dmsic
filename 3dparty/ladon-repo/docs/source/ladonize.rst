Ladonize
========

.. autofunction:: ladon.ladonizer.decorator.ladonize

Access WSGI environ from service methods
----------------------------------------
If you define your service method so it accepts keyword args (**kwargs) you can recieve the environ dict
directly from the WSGI framework that is serving your application. Also some Ladon specific information
is passed via the keyword arguments:

	+------------------------+--------------------------------------------------------------------+
	| Ladon Environ Key      | Description                                                        |
	+========================+====================================================================+
	| LADON_METHOD_TC        | The request specific TypeConverter (dependent on client encodings) |
	+------------------------+--------------------------------------------------------------------+
	| LADON_ACCEPT_LANGUAGES | List of languages accepted by the caller, most important first     |
	+------------------------+--------------------------------------------------------------------+
	| attachments            | Direct access to all request attachments (list)                    |
	+------------------------+--------------------------------------------------------------------+
	| attachments_by_id      | Direct access to all request attachments by id (dict)              |
	+------------------------+--------------------------------------------------------------------+

Example::

	from ladon.ladonizer import ladonize

	class ClientProbeService(object):

			@ladonize(rtype=str)
			def extract_remote_addr(self,**exports):
					"""
					Fetch the client's remote address
					@rtype: The address
					"""
					return exports['REMOTE_ADDR']

In the above example the WSGI environ variable 'REMOTE_ADDR' is used to extract the clients IP-address.

Writing Python 2/3 compatible services
--------------------------------------
Let's study another example::

	from ladon.ladonizer import ladonize
	from firm.customerstore import getCustomerName

	class CustomerService(object):

			@ladonize(int,rtype=unicode)
			def getCustomerName(self,customer_no):
					"""
					Lookup a customer number and resolve the customer name.
					@rtype: The customer name
					"""
					return getCustomerName(customer_no)

The example above is clearly not Python 3 compatible as it uses the unicode type directly.
In Python 3 the type you want to use if you need unicode support is str. Ladon has a simple
solution to this problem if you wish to make use of it. Instead of stating the actual Python
type names (bytes/str/unicode) use the type defines PORTABLE_BYTES and PORTABLE_STRING
from ladon.compat. This will make the Ladon framework resolv string/bytes types according
to the Python version.

So if you use the PORTABLE_STRING definition in your service implementation and start your
service with Python 2 it will resolve to unicode, if you start it with Python 3 it will
resolve to str

Example made portable::

	from ladon.ladonizer import ladonize
	from firm.customerstore import getCustomerName
	from ladon.compat import PORTABLE_STRING

	class CustomerService(object):

			@ladonize(int,rtype=PORTABLE_STRING)
			def getCustomerName(self,customer_no):
					"""
					Lookup a customer number and resolve the customer name.
					@rtype: The customer name
					"""
					return getCustomerName(customer_no)

I the re-written example unicode has been replaced with PORTABLE_STRING. So given that the pseudo module
firm.customerstore is also version independent everything should work.

.. toctree::
   :maxdepth: 2

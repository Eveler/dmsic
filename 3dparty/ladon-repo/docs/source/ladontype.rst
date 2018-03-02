LadonType for complex service types
===================================
.. autoclass:: ladon.types.ladontype.LadonType
   :members: __init__, __dict__

Direct Type Assignment (old-style)
----------------------------------
There are two ways of defining LadonType attributes. Either you can assign an
attribute directly to a type (old-style type-definition) or you can use the
new-style dictionary type-definition.

Using the old-style type-definition means that every attribute in your
LadonType is assigned to a type (primitive or other LadonType) rather than a
value. You can also tell ladon that the attribute should expect a list of
values of a certain type, by assigning the attribute to list containing only
one element; the type to expect::

	balance = float
	transactions = [ Transaction ]

*In the example above example Transaction is another LadonType.*

This is a very nice and clear way to declare a service structure. The downside is that
it offers no way to tell the framework if the attribute is optional, has a
default value, is nullable or to write service documentation on attribute level.

Example::

	class Group(LadonType):
		cn = str
		name = unicode
		description = unicode
		numbers = [int]

	class Person(LadonType):
		uid = str
		name = unicode
		age = int
		groups = [Group]

Portable types
--------------
You can use Ladon's compatability module for LadonTypes the same way as when you define
parameter types with @ladonize. This makes it easier to write Python 2/3 compatible
LadonTypes.

Let's re-write the above example in a portable version::

	from ladon.types.ladontype import LadonType
	from ladon.compat import PORTABLE_STRING,PORTABLE_BYTES

	class Group(LadonType):
		cn = PORTABLE_BYTES
		name = PORTABLE_STRING
		description = PORTABLE_STRING
		numbers = [int]

	class Person(LadonType):
		uid = PORTABLE_BYTES
		name = PORTABLE_STRING
		age = int
		groups = [Group]

Dictionary Type-Definition
--------------------------
The new-style dictionary type-definition allows the service developer to specify
additional attribute properties like default value and whether or not an attribute
can be Null. It also offers the abillity to write documentation for the attribute.

Null and default values
```````````````````````
Let's take a look at nullable values. 

In the following example the attributes "description" and "age" are marked as
nullable, "recieve_newsletter" is not nullable but has a default value that will
be used if the attribute is skipped by the client::

	class Group(LadonType):
		cn = {
			'type': str
		}
		name = {
			'type': unicode
		}
		description = {
			# "description" is nullable, so it is allowed to force Null to this
			# value, if the attribute is skipped it will also be interpreted as Null
			'type': unicode,
			'nullable':True
		}
		numbers = [int]

	class Person(LadonType):
		uid = {
			'type': str
		}
		name = {
			'type': unicode
		}
		age = {
			# "age" is nullable, so it is allowed to force Null to this value,
			# if the attribute is skipped it will also be interpreted as Null
			'type': int,
			'nullable': True
		}
		recieve_newsletter = {
			# Client cannot force Null to this attribute (Ladon will raise a
			# ClientFault exception), but if the attribute is unset it will default
			# to False
			'type': bool,
			'nullable': False,
			'default': False
		}
		groups = [Group]

Reuse code for dictionary type-definition
`````````````````````````````````````````
It is advised that you define common dictionary typedefs so you don't have to rewrite code
for attribute types that have the exact same properties::

	email_typedef = {
		'type': PORTABLE_STRING,
		'nullable': False,
		'doc': 'Enter a valid email address',
	}

	class UserType(LadonType):
		username = email_typedef
		# more attributes go here...

Attribute filter functions
``````````````````````````
Furthermore it is possible to register filter functions for both incoming and outgoing
attribute values which can be used to add validation/modification triggers on certain
attributes. So if you have the attribute "zip_code" in your LadonType and you want to
make sure that users of your service only type in zip-codes from the US. You add a
filter on the attribute's "incoming" filter list that does the check and raises a
clientfault on non-US zip-codes.

In the following example a classic email validation function is registered on the incoming "username" attribute::

	from ladon.ladonizer import ladonize
	from ladon.types.ladontype import LadonType
	from ladon.compat import PORTABLE_STRING,PORTABLE_BYTES
	from ladon.exceptions.service import ClientFault

	import re
	def check_email(email):
		if not re.match('^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$',email):
			raise ClientFault('Invalid email')
		return email
		
	email_typedef = {
		'type': PORTABLE_STRING,
		'nullable': False,
		'doc': 'Enter a valid email address',
		'filters': {
			'incoming': [check_email]
		}
	}

	class UserType(LadonType):
		username = email_typedef
		password = PORTABLE_STRING
		firstname = PORTABLE_STRING
		lastname = PORTABLE_STRING


	class UserService(object):
		@ladonize(UserType,rtype=bool)
		def addUser(self,user):
			# Add user implementation goes here
			return True

Notice in the above example that the filter function is contained in a list. This is because
the Ladon framework can accept multiple filter functions. The filters are executed in the same
order as their placement in the list.

Filter functions can be injected in 4 different points of the RPC process. In the request stage
you can inject filters before and after the Ladon framework parses an attribute, in the response
stage you can inject triggers before and after an attribute is converted to the response object.

	+---------------+-------------------------------------------------------------------+
	| Filter Name   | Description                                                       |
	+===============+===================================================================+
	| incoming_raw  | Applied before the attribute is parsed                            |
	+---------------+-------------------------------------------------------------------+
	| incoming      | Applied after the attribute has been parsed                       |
	+---------------+-------------------------------------------------------------------+
	| outgoing      | Applied before the attriute is converted to response format       |
	+---------------+-------------------------------------------------------------------+
	| outgoing_raw  | Applied after the attribute has been converted to response format |
	+---------------+-------------------------------------------------------------------+

*Note: "outgoing_raw" filters cannot expect that the attribute value type is always the same
because some interfaces require convertion to string format before the final response object
is built.*

.. toctree::
   :maxdepth: 2

Changes
=======
New in 0.9.36
-------------
* Added LOG_JSON_FORMAT

New in 0.9.35
-------------
* Bugfix: MultiPartWriter handles encoding in headers

New in 0.9.33
-------------
* Support for multithreading when running services under ladon-ctl testserve

New in 0.9.31
-------------
* Better hints in LadonType raised exceptions

New in 0.9.30
-------------
* Bugfix: When posting multi-part attachments with no content-id no delete was performed. This is fixed

New in 0.9.26
-------------
* Fixed bug in multiparthandler.py, Boundary sometimes came in with quotes.
* Fixed bug when exception occured in wsgi_application.

New in 0.9.25
-------------
* Added possibility to add headers and cookies to client init and method calls.

New in 0.9.24
-------------
* BUGFIX: Probed Language should not be passed to interface description method

New in 0.9.23
-------------
* Added LADON_ACCEPT_LANGUAGES to keyword args, service methods can use this to get a list of languages accepted by the user.

New in 0.9.22
-------------
* Hint added to fault requests

New in 0.9.21
-------------
* Path fix for built-in skins

New in 0.9.20
-------------
* Python JSONWSPClient: Get description with HTTP GET method

New in 0.9.19
-------------
- Support for interface aliasing
- interface soapdocumentliteral also accessible via soap

New in 0.9.18
-------------
- Small font change
- Fixed albumservice example

New in 0.9.17
-------------
- jsonwspclient.js: Catch non-JSON responses send serverfault callback to client call-point
- "bluebox" skin: present server faults as well as service faults
- "bluebox" skin: present request status code and text

New in 0.9.16
-------------
Added ladon-ctl She-Bang

New in 0.9.15
-------------
Package data support for both pip and easy_install

New in 0.9.12
-------------
- fixed path problem in LadonWSGIApplication

New in 0.9.11
-------------
Added built-in skins "bluebox" and "rounded"

New in 0.9.10
-------------
- Added som front-page documentation
- Added examples and docs to source package via (MANIFEST.in)
- Changed theme for documentation to "bootstrap"

New in 0.9.9
------------
- Fix: Version 0.9.0 broke Python 3 support. This has now been fixed and tested with Python 3.4

New in 0.9.8
------------
- Finally introducing Tasks. Earlier on it has been announced that task-type Ladon methods would be the
  feature that brings Ladon to version 1.0.0. Indeed that will be the case, but this is kind of a technology
  preview.
- Cave-eats:
	- Uses the threading module meaning that GIL is in play
	- Task state is kept in global python variables and therefore do not work cross-host nor cross-process

In many use-cases these cave-eats are not a problem. Ie. if your task spawns a new synchronious process
like a system-call you will not be having problems with GIL and the current implementation will work as
long as your application stays within the same process.

The good thing about the current solution is that it works out-of-the-box without introducing thirdparty
state-keeping services. It should also be noted that if you are using ie. mod-wsgi on apache2 it is
possible to control process groups for specific Ladon services, so you can configure your apache server
to use only one process for your services containing task type Ladon methods, and multiple procesesses for
your other services that do not need to keep state like Ladon tasks.

The solution for the cave-eats mentioned will be the option to configure socket-based state caching like
memcached or redis. If using the thirdparty state caching option Ladon will shift over to using the
multiprocessing module for task execution. This solution should solve both cave-eats and will be when
Ladon turns into 1.0.0.

The current implementation will probably stay in Ladon because it is very easy to use and requires no
extra configuration other than the keyword in your ladonize decorator - example::

	from ladon.compat import PORTABLE_STRING
	from ladon.ladonizer import ladonize

	class TaskService(object):

		@ladonize(PORTABLE_STRING, int, rtype=int, tasktype=True)
		def taskExample(self,session_id,counter,**kw):
			repeat = 5.0
			for i in xrange(int(repeat)):
				time.sleep(5)
				kw.get('update_progress')(float(i+1.0)/repeat)
			return counter

Ladon tasks `documentation`_

.. _Documentation: https://pythonhosted.org/ladon/tasks.html

New in 0.9.3
------------
- Added set_log_backup_count(), set_log_maxsize()


New in 0.9.2
------------
- Added __version__ to ladon package

New in 0.9.1
------------
- Changes to jsonwsp interface:
	- Documentation lines in description are default turned off from this version on.
	  Force documentation lines into the description by passing include_doc=true into the query string
	- Description is now cached in memory per service per thread.

New in 0.9.0
------------
- Added reserved root path  "skins". If the path preceded with "skins" leads to an existing file it will be
  sent back raw. This makes it possible to add javascripts, images and css files to custom skins.
- Added bluebox with invokable service UI to "examples/appearance"

New in 0.8.8
------------
- Fix: Python3 support for LadonType methods

New in 0.8.7
------------
- Fix: The request dictionary was not being expanded while debugging

New in 0.8.6
------------
- Debug logging request args now as req_dict

New in 0.8.5
------------
- Better exception logging

New in 0.8.4
------------
- Fixed issues with soap and xmlrpc protocols, so they can load on Python 3 (no call-tests made)
- Added internal logging of calls to ladonized methods. This feature logs timestamp, execution time
  service- and method names, positional- and keyword args, return value and exceptions if they occur.
  To enable this feature set loglevel to minimum 6 (debug level): ladon.tools.log.set_loglevel()

New in 0.8.3
------------
- Added the ability to set the logfile to log to: from ladon.tools.log import set_loglevel,set_logfile

New in 0.8.2
------------
- Replaced oldest SOAP implementation with a contributed implementation with document literal. This version works
  with Microsofts .Net SOAP client.
- Added possibility to use mirror/reflection mechanism on faults so it is possible to trace errors.

New in 0.8.1
------------
- Added reflection to fault response objects so it is possible to trace faults back to specific requests

New in 0.8.0
------------
- Added the optional key to method params info in JSONWSP/description. It was somehow removed during previous update.

New in 0.7.9
------------
- Argument default values added to the JSONWSP/description

New in 0.7.7
------------
- possibility to add styles globally by adding css-files in a folder called "skins" which should be found in your Ladon path
	- Add extra styles for the catalog page: skins/catalog-extra.css
	- Add extra styls for service pages: skins/service-extra.css
- Fixed a problem with service class doc. All lines in the class documentation were stripped making it impossible to write reStructuredText directives. now using inspect.cleandoc()


New in 0.7.6
------------
- wsgi_application now responds to @publisher keyword for service and parameter documentation
- JSONWSPClient: Added the ability to add request headers manually via member dict JSONWSPClient.extra_headers

New in 0.7.3
------------
- Added service-wide logging fascilities via LadonWSGIApplication's constructor. Preliminary log levels are:
	- ladon.server.NO_LOGGING = 0
	- ladon.server.LOG_REQUEST_ACCESS = 1
	- ladon.server.LOG_REQUEST_DICT = 2
	- ladon.server.LOG_RESPONSE_DICT = 4
	- ladon.server.LOG_EXECUTION_TIME = 8

New in 0.7.2
------------
- Added the possibility to use choose between different publishing types when writing
  inline documentation for the online API documentation. Possible publishers are "raw",
  "pre" and "docutils" - Example::

	@ladonize([PORTABLE_STRING], rtype=[File])
	def download(self,names):
		"""
		@publisher: docutils
		
		- Test
		- Test 2
		
		+------------+------------+-----------+ 
		| Header 1   | Header 2   | Header 3  | 
		+============+============+===========+ 
		| body row 1 | column 2   | column 3  | 
		+------------+------------+-----------+ 
		| body row 2 | Cells may span columns.| 
		+------------+------------+-----------+ 
		| body row 3 | Cells may  | - Cells   | 
		+------------+ span rows. | - contain | 
		| body row 4 |            | - blocks. | 
		+------------+------------+-----------+
		
		Kode eksempel::
			
			def test(self):
				print "oijfwe"
		
		

		Download multiple files at once. For each name in the <b>names</b> the service
		attempts to find a file in service/upload that matches it. If a name does not
		have a matching file it is ignored.
		
		@param names: A list of the file names
		@rtype: Returns a list of File objects
		"""
		global upload_dir
		response = []
		for name in names:
			f = File()
			f.name = name
			f.data = attachment(open(join(upload_dir,name),'rb'))
			response += [f]
		return response

New in 0.7.1
------------
Fixed bug 974655
Added via proxy feature to the Python jsonwsp client

New in 0.7.0
------------
Fixed bugs 926442 and 926445

New in 0.6.7
------------
- Attribute filtering is a new feature that allows the service developer to define functions
  that can be triggered before and after a service method has been executed. `Filter functions`_
  can be used to validate or modify attribute values.

.. _Filter functions: http://packages.python.org/ladon/ladontype.html#reuse-code-for-dictionary-type-definition

New in 0.6.6
------------
- New dictionary based type-definition for LadonType attributes. Until version 0.6.6 all
  LadonType attributes had to reference a type or list of type directly. With dictionary type
  definitions it is possible for the service developer to pass more detailed properties about
  attributes, like documentation lines, default value or whether it is nullable (None) or not.
  Old-style LadonType attribute definitions are still valid and therefore this change offers
  backwards compatability. The integration of nullable is built into the soap and jsonwsp
  interfaces. Example::

	class Person(LadonType):
		username = PORTABLE_BYTES     # old-style
		groups = [ PORTABLE_BYTES ]
		mobile = {                    # new-style
			'type': PORTABLE_BYTES,
			'nullable': True,
			'doc': "User's mobile number." }
		valid_user = {
			'type': bool,
			'nullable': False,
			'default': False,
			'doc': ['Is user valid.','If not given, the user is invalid.'] }

New in 0.6.5
------------
- Fault handling finally implemented. interfaces must now implement a FaultHandler inheriting
  the BaseFaultHandler class. Fault handlers have been implemented for both SOAP and JSONWSP
  interfaces.
  All exceptions that occure under method invocation are caught by Ladon's dispatcher and
  sent to the interface fault handler. Use ServerFault or ClientFault exceptions implemented in
  ladon.exceptions.service to raise either a server fault or to blame a fault on the client.
  Other exceptions that might occure under service method invocation are viewed as unmanaged
  Server Faults, and converted to such by the dispatcher.

- New attachment reference format cidx:<index>. This format let's the client post request that
  have references to attachment parts by index rather than Content-Id.

New in 0.6.4
------------
- JSONWSPClient __init__(description=None,url=None) takes description url as first argument or
  keyword "description". A new keyword argument "url" can be passed instead of description if
  the jsonwsp API is known. The tradeoff of using the url is that there are not created any
  placeholder methods on the JSONWSPClient object, instead you must call methods via the
  call_method() method.
- CustomResponse - Ladon now offers the ability to define custom response on specified methods.
  For instance you can make Ladon respond with a browser download response on a specific service
  method. Example::

	class HTTPAttachmentResponse(CustomResponse):
		def __init__(self,fileobj,filename,filesize,blocksize=4096):
			self.fileobj = fileobj
			self.filename = filename
			self.filesize = filesize
			self.blocksize = blocksize
		
		def response_headers(self):
			# TODO: Handle encodings for filenames
			return [
				('Content-Disposition','attachment; filename="%s"' % self.filename.encode('utf-8')),
				('Content-Type','application/force-download'),
				('Content-Length',str(self.filesize))]
		
		def response_data(self):
			return iter(lambda: self.fileobj.read(self.blocksize), '')

- Bug 852234 - Removed nillable and minOccurs attributes from SOAP part elements.
- Bug 861193 - Removed '_' to '-' conversion for complexType elements.
- Bug 884431 - Fixed boolean type on SOAP response objects.

New in 0.6.3
------------
- Nicer query-string handling in wsgi_application.py
- API Browser templates use a form with GET-request to change skins
  rather than the SELECT's onchange.
- Added proper HTTP return code and Accept value for empty requests to
  service interfaces
- Fixed POST conversion of dashes to underscores in SOAP requests

New in 0.6.2
------------
- Bug 831553 - Better probing for incomming client URI's
- Question 168374 - Completely rewrite of the SOAPRequestHandler, 
  fixing a yet unreported bug with arrays and introducing support
  for incomming prettyfied XML.

New in 0.6.1
------------
- The major enhancement is support for attachments in the Ladon framework. Read more
  about Ladon attachments on: `Server attachments`_
- JSON-WSP Client has built-in support for attachments: `Client attachments`_
- JSON-WSP Client supports Python 3
- New default skin for the `API browser`_
- Support for `custom skinning`_
- Better Python 3 support in general
- ladonctl subcommand "serve" altered to "testserve"
- Bug fixes: 808331, 821923

.. _Server attachments: http://ladonize.org/index.php/Ladon_Attachments
.. _Client attachments: http://ladonize.org/index.php/Ladon_Attachments#Send_and_recieve_attachments_using_Ladon.27s_JSON-WSP_client
.. _API browser: http://ladonize.org/python-demos/AlbumService
.. _custom skinning: http://ladonize.org/index.php/Ladon_Custom_Skins

New in 0.5.1
------------
- Added cross-version compatible ladon-ctl shell script. This script will have
  several sub-commands over time. The first and only command is "serve" to
  quickly test one or more service modules.

New in 0.5.0
------------
- Experimental Python 3 support
- Dropped Cheetah in favor of jinja2 due to lack of Python 3 support in Cheetah
- Added compat module that handles python 2/3 compatability issues for types
- Added unittests for string integrity

New in 0.4.8
------------
- Added types to the browser based service navigation interface

New in 0.4.7
------------
- Service Navigation: Better browser navigation for services. New features
  are full service documentation with CSS-styled browsable interface.
  
- Much more documentation

New in 0.4.6
------------
- Added export_dict to the dispatcher. Values from this dict will be exported
  to ladonized methods if they have \*\*kw at the end of their parameter list.
  By default the LadonWSGIApplication will export WSGI's environ.
- Much more documentation

New in 0.4.5
------------
- Moved jsonwspclient.py into the ladon package in subpackage clients::

	from ladon.clients.jsonwsp import JSONWSPClient

New in 0.4.4
------------
- Removed old-style method invoking from the jsonwspclient javascript client
- Added a JSON-WSP python client: misc/jsonwsp/jsonwspclient.py. The client
  can be integrated into other python modules using the JSONWSPClient class,
  but it can also be run as a shell command.

New in 0.4.3
------------
- New feature called mirror/reflection especially designed for asynchronious
  client/server communication to keep track on the client which responses
  belongs to which requests. For example a request ID can be mirrored by the
  server and reflected back to the client, so it is possible to map many
  simultaneously incomming responses that are handled by the same function.
- Ladon documentation for the dispatcher

New in 0.4.2
------------
- Fixed bug that made incomming booleans always resolve to True
- Ladon documentation for collection and typeconverter

New in 0.4.1
------------
- Added LGPL License.txt in the root of the project
- Ladon documentation for ladonize

New in 0.3.7
------------
- jsonwsp.spec file added to the repository.
- jsonwsp description specification very near 1.0
- Bug-fix in wsgi_application.py charset detection moved to the first action
  when a request is recieved.
- Added jsonwsp javascript client that can parse jsonwsp/description objects
  and invoke methods on services as function calls.

New in 0.3.6
------------
- jsonrpc interface renamed to jsonwsp, short for JSON Web Service Protocol.
  This was decided to prevent confusing whether Ladon's json-based protocol
  supports the json-rpc specified in at: http://json-rpc.org/. Ladon's json-
  based protocol is clearly inspired by json-rpc, but is not the same.

- jsonwsp response, request and description formats has been altered to contain
  'type' and 'version' values.

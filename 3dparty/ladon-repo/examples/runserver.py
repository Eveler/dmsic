# -*- coding: utf-8 -*-
from ladon.server.wsgi import LadonWSGIApplication
import wsgiref.simple_server
from os.path import normpath,abspath,dirname,join
from ladon.tools.log import set_loglevel,set_logfile,set_log_backup_count,set_log_maxsize
set_logfile(join(dirname(normpath(abspath(__file__))),'examples.log'))
set_loglevel(4) # debug
set_log_backup_count(50)
set_log_maxsize(50000)

scriptdir = dirname(abspath(__file__))
service_modules = ['calculator','albumservice','transferservice','shopservice','taskservice']

# Create the WSGI Application
application = LadonWSGIApplication(
	service_modules,
	[join(scriptdir,'services'),join(scriptdir,'appearance')],
	catalog_name = 'Ladon Service Examples',
	catalog_desc = 'The services in this catalog serve as examples to how Ladon is used',
	logging=31)

if __name__=='__main__':
	# Starting the server from command-line will create a stand-alone server on port 8080
	port = 8080
	print("\nExample services are running on port %(port)s.\nView browsable API at http://localhost:%(port)s\n" % {'port':port})

	server = wsgiref.simple_server.make_server('', port , application)
	server.serve_forever()

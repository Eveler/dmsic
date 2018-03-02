from ladon.server.wsgi import LadonWSGIApplication
from os.path import normpath,abspath,dirname,join
from ladon.tools.log import set_loglevel,set_logfile,set_log_backup_count,set_log_maxsize
set_logfile(join(dirname(normpath(abspath(__file__))),'apache-examples.log'))
set_loglevel(6) # debug
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

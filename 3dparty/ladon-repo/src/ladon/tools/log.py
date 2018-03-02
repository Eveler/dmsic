# -*- coding: utf-8 -*-
"""
Setup the loglevel for services on this particular server.

When the system calles the log function write() it is always associated with a
log-level. Whether or not the log-line reaches all the way to the syslog depends
on the current loglevel configuration.

The main log function is called write(). It logs by default in level 3 if not
overridden with the loglevel keyword argument.

Log-levels::
	Error levels:
	1 = Critical error (unimplemented resolution and undefined consequences)
	2 = Elevated error (high priority error)
	3 = Normal error
	
	Info level:
	4 = Info           (Log brief remarks about successful operations)
	
	Debug levels:
	5 = Notices        (inline log messages for tracing problems)
	6 = Debug          (manual tracing)
	7 = trace          (trace details)
"""

import os,logging,logging.handlers
import sys,traceback
if sys.version_info[0]==2:
	from StringIO import StringIO
elif sys.version_info[0]>=3:
	from io import StringIO

__author__ = "Jakob Simon-Gaarde <jakob@simon-gaarde.dk>"

cur_loglevel = 4

def get_traceback():
	strio = StringIO()
	traceback.print_exc(file=strio)
	return strio.getvalue()

def set_loglevel(level):
	global cur_loglevel
	cur_loglevel = level

def get_loglevel():
	global cur_loglevel
	return cur_loglevel

cur_logfile = '/tmp/ladon.log'
def set_logfile(logfile):
	global cur_logfile
	cur_logfile = logfile

cur_log_maxsize = 4000000
def set_log_maxsize(log_maxsize):
	global cur_log_maxsize
	cur_log_maxsize = log_maxsize

cur_backup_count = 5
def set_log_backup_count(backup_count):
	global cur_backup_count
	cur_backup_count = backup_count

def write(msg,loglevel=3,context=None,force=False):
	
	"""
	Maybe write a message to the syslog. If no loglevel is passed the default level is 3.
	
	Log-levels::
		Error levels:
		1 = Critical error (unimplemented resolution and undefined consequences)
		2 = Elevated error (high priority error)
		3 = Normal error
		
		Info level:
		4 = Info           (Log brief remarks about successful operations)
		
		Debug levels:
		5 = Notices        (inline log messages for tracing problems)
		6 = Debug          (manual tracing)
		7 = Trace          (trace details)
	"""
	global cur_loglevel,cur_logfile,cur_backup_count,cur_log_maxsize

	if cur_loglevel<loglevel and force==False:
		# Log level filters out this message
		return

	try:
		remote_host = os.environ['LADON_REMOTE_HOST']
		LOG_FILENAME = '%s.%s' % (cur_logfile,remote_host)
		logger = logging.getLogger('ladonlogger.%s' % remote_host)
	except:
		LOG_FILENAME = cur_logfile
		logger = logging.getLogger('ladonlogger')

	logger.setLevel(logging.DEBUG)

	# Add the log message handler to the logger
	if len(logger.handlers)==0:
		handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=cur_log_maxsize, backupCount=cur_backup_count)
		formatter = logging.Formatter("%(asctime)s - %(message)s")
		handler.setFormatter(formatter)
		logger.addHandler(handler)

	logger.debug(msg)


def info(msg,context=None,force=False):
	"""
	Send a brief remark to the syslog upon successful operations. Info will only reach the syslog if the current
	loglevel configuration is set to 4 or more.
	"""
	write(msg,4,context,force)


def notice(msg,context=None,force=False):
	"""
	Send a notice to the syslog. Notices will only reach the syslog if the current
	loglevel configuration is set to 5 or more.
	"""
	write(msg,5,context,force)

def debug(msg,context=None,force=False):
	"""
	Send a debug message to the syslog. Debug messages will only reach the syslog if the current
	loglevel configuration is set to 6 or more.
	"""
	write(msg,6,context,force)

def trace(msg,context=None,force=False):
	"""
	Send a debug message to the syslog. Debug messages will only reach the syslog if the current
	loglevel configuration is set to 6 or more.
	"""
	write(msg,7,context,force)

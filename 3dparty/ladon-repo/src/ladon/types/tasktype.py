# -*- coding: utf-8 -*-
from wsgiref.util import request_uri
from ladon.types.ladontype import LadonType
import ladon.tools.log as log
import inspect,time
from ladon.tools.threadmanagement import ManagedThread,thread_count,get_thread_info,set_thread_info,thread_running
from ladon.exceptions.service import ServerFault

class TaskInfoResponse(LadonType):
	task_id = {
		'type': int,
		'doc': u'unique integer identifying the task to that has been created'
	}

class TaskProgressResponse(LadonType):
	task_id = {
		'type': int,
		'doc': u'unique integer identifying the task to that has been probed'
	}
	progress = {
		'type': float,
		'doc': u'Floating point value between 0 and 1 denoting the progress in percent'
	}
	duration = {
		'type': float,
		'doc': u'Floating point value that informs how long time in seconds the task as run'
	}
	starttime = {
		'type': float,
		'doc': u'The start time in seconds since the epoch as a floating point number'
	}

taskProgress_args = (int,)
taskProgress_kw = {
	'rtype': TaskProgressResponse
}

taskProgress_kw = {
	'rtype': TaskProgressResponse
}

class TaskRunner(ManagedThread):
	def __init__(self,method,args,kw):
		self.method = method
		self.args = args
		self.kw = kw
		super(TaskRunner,self).__init__()
		
	def run_managed(self):
		argspecs = inspect.getargspec(self.method)
		try:
			if argspecs.keywords!=None:
				res = self.method(*(self.args),**(self.kw))
			else:
				res = self.method(*(self.args))
			set_thread_info(self.thread_id, 'result', res)
		except Exception as e:
			set_thread_info(self.thread_id, 'exception', log.get_traceback())
			log.write("Thread ID: %d (%s) failed with the following exception:\n%s" % (self.thread_id,self.__class__,log.get_traceback()))
			raise e

def taskStarter(self, *args, **kw):
	task_method = getattr(self,"_task_%s" % kw['LADON_METHOD_NAME'])
	tr = TaskRunner(task_method,args,kw)
	kw['update_progress'] = tr.update_progress
	tr.start()
	tir = TaskInfoResponse()
	tir.task_id = tr.thread_id
	return tir

def taskProgress(self, task_id):
	tpr = TaskProgressResponse()
	tpr.task_id = task_id
	tpr.progress = get_thread_info(task_id,'progress')
	if tpr.progress==None:
		raise ServerFault("Task ID: %d does not seem to exist" % task_id)
	tpr.starttime = get_thread_info(task_id,'start')
	stoptime = get_thread_info(task_id,'stop')
	tpr.duration = (stoptime if stoptime else time.time()) - get_thread_info(task_id,'start')
	return tpr

def taskResult(self, task_id):
	exc = get_thread_info(task_id, 'exception')
	if exc:
		raise ServerFault("Error occured while executing task_id: %d" % task_id,exc)
	res = get_thread_info(task_id, 'result')
	if res:
		return res
	else:
		if thread_running(task_id):
			raise ServerFault("Task ID: %d has no result because it is still running" % task_id)
		else:
			raise ServerFault("Task ID: %d has no result and is not running either" % task_id)


from threading import Lock,Thread
import traceback,sys,time
import ladon.tools.log as log

def get_traceback():
	strio = StringIO()
	traceback.print_exc(file=strio)
	return strio.getvalue()

thread_id_locker = Lock()
common_lock = Lock()

thread_dict = {
	'running': [],
	'done': [],
	'thread_info': {}
}

thread_id = 0

def next_thread_id():
	global thread_id,thread_id_locker
	thread_id_locker.acquire()
	thread_id += 1
	thread_id_locker.release()
	return thread_id

def update_thread_dict(thread_id,running):
	global thread_dict,common_lock
	common_lock.acquire()
	if running:
		if thread_id not in thread_dict['running']:
			thread_dict['running'] += [thread_id]
			try:
				thread_dict['done'].remove(thread_id)
			except ValueError as e:
				pass
	else:
		if thread_id not in thread_dict['done']:
			thread_dict['done'] += [thread_id]
			try:
				thread_dict['running'].remove(thread_id)
			except ValueError as e:
				pass
		
	common_lock.release()

def thread_count(running):
	global thread_dict,common_lock
	common_lock.acquire()
	tcnt = len(thread_dict['running' if running else 'done'])
	common_lock.release()
	return tcnt

def thread_running(thread_id):
	global thread_dict,common_lock
	common_lock.acquire()
	running = thread_id in thread_dict['running']
	common_lock.release()
	return running

def set_thread_info(thread_id,key,value):
	global thread_dict,common_lock
	common_lock.acquire()
	if thread_id not in thread_dict['thread_info']:
		thread_dict['thread_info'][thread_id] = {}
	thread_dict['thread_info'][thread_id][key] = value
	common_lock.release()

def get_thread_info(thread_id,key):
	global thread_dict,common_lock
	common_lock.acquire()
	val = thread_dict['thread_info'].get(thread_id,{}).get(key,None)
	common_lock.release()
	return val

def listappend_thread_info(thread_id,key,value):
	global thread_dict,common_lock
	common_lock.acquire()
	if thread_id not in thread_dict['thread_info']:
		thread_dict['thread_info'][thread_id] = {}
	l = thread_dict['thread_info'][thread_id].get(key,None)
	if not l:
		thread_dict['thread_info'][thread_id][key] = []
	thread_dict['thread_info'][thread_id][key].append(value)
	common_lock.release()

def setitem_thread_info(thread_id,key,dictkey,value):
	global thread_dict,common_lock
	common_lock.acquire()
	if thread_id not in thread_dict['thread_info']:
		thread_dict['thread_info'][thread_id] = {}
	l = thread_dict['thread_info'][thread_id].get(key,None)
	if not l:
		thread_dict['thread_info'][thread_id][key] = {}
	thread_dict['thread_info'][thread_id][key][dictkey] = value
	common_lock.release()

def thread_info(thread_id,key):
	global thread_dict,common_lock
	common_lock.acquire()
	val = thread_dict['thread_info'].get(thread_id,None)
	if not val==None:
		val = val.get(key,None)
	common_lock.release()
	return val

def all_thread_info_keys():
	global thread_dict,common_lock
	common_lock.acquire()
	keys = list(thread_dict['thread_info'])
	common_lock.release()	
	return keys

class ManagedThread(Thread):
	
	def post_event(self,identifier,*args,**kw):
		if self.event_cb:
			self.event_cb(identifier,*args,**kw)

	def __init__(self):
		self.thread_id = next_thread_id()
		if not getattr(self,'event_cb',None):
			self.event_cb = None
		super(ManagedThread,self).__init__()
	
	def run_managed(self):
		raise NotImplementedError
	
	def run(self):
		update_thread_dict(self.thread_id,True)
		self.update_progress(0.0)
		self.set_thread_info('start',time.time())
		try:
			self.run_managed()
		except:
			update_thread_dict(self.thread_id,False)
			log.write("Thread ID: %d (%s) failed with the following exception:\n%s" % (self.thread_id,self.__class__,log.get_traceback()))
		self.set_thread_info('stop',time.time())
		self.update_progress(1.0)
		update_thread_dict(self.thread_id,False)
	
	def update_progress(self,progress):
		if type(progress)!=float:
			return
		if progress>1:
			progress = 1
		if progress<0:
			progress = 0
		self.set_thread_info('progress',progress)
	
	def progress(self):
		self.get_thread_info('progress',progress)
		
	def set_thread_info(self,key,val):
		set_thread_info(self.thread_id,key,val)

	def get_thread_info(self,key):
		return get_thread_info(self.thread_id,key)

	def listappend_thread_info(self,key,val):
		return listappend_thread_info(self.thread_id,key,val)
	
	def setitem_thread_info(self,key,dictkey,val):
		return setitem_thread_info(self.thread_id,key,dictkey,val)

	def thread_info(self,key):
		return thread_info(self.thread_id,key)
 

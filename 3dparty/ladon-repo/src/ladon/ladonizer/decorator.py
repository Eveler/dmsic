# -*- coding: utf-8 -*-

"""
This module contains the entry-point for all Ladon Service methods.
Every method that should be exposed to the interfaces supported in
a given Ladon installation must register itself through the ladonize
decorator.
"""

__author__ = "Jakob Simon-Gaarde"

from ladon.ladonizer.collection import global_service_collection
from ladon.types import validate_type,expand_value,result_to_dict
from ladon.exceptions.ladonizer import *
import ladon.tools.log as log
import time
import types

def ladonize(*def_args,**def_kw):
	"""
	The entry-point for all Ladon service methods. You could call
	this the magic-decorator that does initiates all the parsing
	analysing and pre-storing of service method capabilities and
	requirements.
	The ladonize decorator takes exactly the same amount of
	arguments as the method it is decorating plus one mandatory
	keyword argument *rtype* that type-defines the return type of
	the method. 
	Each argument given to the decorator type-defines the order-
	wise corresponding parameter of the method being decorated::
		
		class SessionService(object):
		
			@ladonize(str,str,rtype=str)
			def login(self,username,password):
				...
				...
				return session_id

	There are a couple of optional keyword arguments to ladonize
	aswell:
		+-------------------------+------------------------------------------------------------------------------------+
		| keyword arg             | Description                                                                        |
		+=========================+====================================================================================+
		| encoding                | Control the encoding to be used internally in the service method for raw strings   |
		+-------------------------+------------------------------------------------------------------------------------+
		| allow_unsafe_conversion | True means that Ladon will try to convert arguments and return values if nessecary |
		+-------------------------+------------------------------------------------------------------------------------+
		| tasktype                | If tasktype is True Ladon will execute the method in background and add 2 extra\   |
		|                         | methods: *<method_name>_progress* and *<method_name>_result* to monitor the tasks\ |
		|                         | progress and retrieve the final result respectively.                               |
		+-------------------------+------------------------------------------------------------------------------------+
	"""
	def decorator(f):
		def injector(*args,**kw):
			"""
			The Ladon inner injection function is called from the dispatcher. It does run-time type
			checking against the types registered with the service method. If everything is OK the
			user method is called. The result of the userspace-method is then checked before it is
			passed back to the dispatcher.
			"""
			
			if def_kw.get('tasktype',False)==True:
				return f(*args,**kw)
			
			# Get the LadonMethodInfo object generated at parsetime which is stored as a member
			# on the function object
			lmi = injector._ladon_method_info
			# Reference the incomming arguments in callargs (filter out the function reference)
			callargs = args[1:]
			
			for argidx in range(len(callargs)):
				# Check the type of each argument against the type which the method has been 
				# registered to take in the order-wise corresponding argument
				if not validate_type(lmi._arg_types[argidx],callargs[argidx]):
					# Raise ArgTypeMismatch
					raise ArgTypeMismatch(
						lmi.sinfo,
						lmi._func_name,
						lmi._arg_names[argidx],
						lmi._arg_types[argidx],
						type(callargs[argidx]))
			
			# Call the userspace service method (**kw will be used to transport Ladon info
			# and tools all the way to userspace of the service method. I.e. the TypeConverter
			# is passed with the keyword "LADON_METHOD_TC")
			debug_mode = log.get_loglevel()>=6
			if debug_mode:
				# Build a request_dict for debugging
				req_dict = {}
				for argidx in range(len(callargs)):
					req_dict[lmi._arg_names[argidx]] = expand_value(callargs[argidx],lmi._arg_types[argidx],service_name=lmi.sinfo.servicename,method_name=lmi._func_name)
				log_line = [
					'Method:%s.%s' % (lmi.sinfo.servicename,lmi._func_name),
					'RequestArgs:%s' % str(req_dict),
					'RequestKeywordArgs:%s' % str(kw)]
			
			if debug_mode:
				try:
					start = time.time()
					res = f(*args,**kw)
					log_line.insert(0,'ExecutionTime:%s' % str(time.time()-start))
				except Exception as e:
					log_line += ['Exception:%s' % str((log.get_traceback(),)) ]
					log.debug('\t%s' % ('\t'.join(log_line)))
					raise e
				
				log_line += [ 'ReturnValue:%s' % str(result_to_dict(lmi,res)) ]
				log.debug('\t%s' % ('\t'.join(log_line)))
				
			else:
				res = f(*args,**kw)
			# Check the return type
			if not validate_type(lmi._rtype,res):
				# Raise Arg-type mismatch 
				raise ReturnTypeMismatch(lmi.sinfo,lmi._func_name,lmi._rtype,type(res))
			
			# Return the result to the dispatcher
			return res
		
		# Register the service method and all the types required by it 
		ladon_method_info = global_service_collection().add_service_method(f,*def_args,**def_kw)
		
		# store the LadonMethodInfo object directly on the fuction object
		injector._ladon_method_info = ladon_method_info
		injector.__doc__ = ladon_method_info._doc
		injector.func_name = ladon_method_info._func_name
		return injector
		
	return decorator 

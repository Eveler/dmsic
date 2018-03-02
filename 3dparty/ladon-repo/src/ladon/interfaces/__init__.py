# -*- coding: utf-8 -*-
import sys,imp,os,inspect
from ladon.exceptions.interfaces import *
from ladon.interfaces.base import BaseInterface
from ladon.compat import PORTABLE_STRING_TYPES

_interfaces = {}

#def install(mod,path=None):
	#global _exposers
	#if [str,unicode].count(type(path)):
		#search_path += [path]
	#elif [list,tuple].count(type(path)):
		#search_path += list(path)
	#search_path = sys.path + [os.path.dirname(__file__)]
	#fp, pathname, description = imp.find_module(mod,search_path)
	#if _exposers.has_key(pathname):
		#return
	#try:
		#impmod = imp.load_module(mod,fp,pathname,description)
		#_exposers[pathname] = impmod
	#except Exception, e:
		#raise ImportExposerException(mod,pathname,str(e))


def expose(class_type):
	"""
	This is a decorator for service interfaces. It basically checks that
	the interface classes which are exposed meets the requirements for
	interface implementations.
	It adds the interface to a global interface-cache.
	All default ladon interfaces are added using this decorator, if you are
	extending Ladon with a new interface use this decorator.
	Requirements:
	------------
	Interfaces must inherit the ladon.interfaces.base.BaseInterface class.
	"""
	global _interfaces
	if inspect.getmro(class_type).count(BaseInterface):
		if_names = class_type._interface_name()
		if type(if_names) in PORTABLE_STRING_TYPES:
			if_names = [ if_names ]
		if type(if_names) not in [list,tuple]:
			raise ExposeInterfaceException(class_type.__name__,"wefew",'Interfaces must implement the static _interface_name method to return a unique string or list of strings identifying the interface.')
		for if_name in if_names:
			if type(if_name) not in PORTABLE_STRING_TYPES:
				raise ExposeInterfaceException(class_type.__name__,"wefew",'Interfaces must implement the static _interface_name method to return a unique string or list of strings identifying the interface.')
			if if_name in _interfaces:
				raise ExposeInterfaceException(class_type.__name__,"wefwe",'The interface name is already being used by anothere interface.')
			_interfaces[if_name] = class_type
	return class_type


def accept_basetype(typ):
	global _interfaces
	result_interfaces = []
	for k,v in _interfaces.items():
		if v._accept_basetype(typ):
			result_interfaces += [v]
	return result_interfaces

def accept_list():
	global _interfaces
	result_interfaces = []
	for k,v in _interfaces:
		if v._accept_list():
			result_interfaces += [v]
	return result_interfaces

def name_to_interface(ifname):
	global _interfaces
	if ifname in _interfaces:
		return _interfaces[ifname]
	return None


import ladon.interfaces.soap
import ladon.interfaces.soap11
import ladon.interfaces.jsonwsp
import ladon.interfaces.jsonrpc10
import ladon.interfaces.xmlrpc

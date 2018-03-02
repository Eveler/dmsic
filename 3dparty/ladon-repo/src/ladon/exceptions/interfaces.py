# -*- coding: utf-8 -*-

from ladon.exceptions.base import LadonException

class ExposerException(LadonException):
	def __init__(self,name,path):
		LadonException.__init__(self)
		self.name = name
		self.path = path

class ExposeInterfaceException(ExposerException):
	def __init__(self,name,path,error_str):
		ExposerException.__init__(self,name,path)
		self.error_str = error_str

	def __str__(self):
		return 'An error occured while exposing the Ladon interface "%s" at "%s". %s' % \
			(self.name,self.path,self.error_str)

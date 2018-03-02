# -*- coding: utf-8 -*-

from ladon.ladonizer import ladonize
from ladon.compat import PORTABLE_STRING
import socket

class OperatingSystem(object):

	@ladonize(rtype=PORTABLE_STRING)
	def getHostName(self):
		return PORTABLE_STRING(socket.gethostname())

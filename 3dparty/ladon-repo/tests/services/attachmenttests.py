# -*- coding: utf-8 -*-
from ladon.ladonizer import ladonize
from ladon.types.attachment import attachment
from ladon.types.ladontype import LadonType
from ladon.compat import PORTABLE_STRING

class File(LadonType):
	name = PORTABLE_STRING
	data = attachment

class UploadFileResponse(LadonType):
	name = PORTABLE_STRING
	file_size = int

class Album(LadonType):
	title = PORTABLE_STRING
	tracks = [attachment]

class UploadAlbumResponse(LadonType):
	title = PORTABLE_STRING
	track_sizes = [int]

class AttachmentTestService(object):
	
	@ladonize(int,[attachment],rtype=int)
	def recieveAttachment(self,number,incomming,**kw):
		a=incomming[0].read()
		return len(a)

	@ladonize(File,rtype=UploadFileResponse)
	def uploadFile(self,data,**kw):
		res = UploadFileResponse()
		res.name = data.name
		res.file_size = len(data.data.read())
		return res

	@ladonize(Album,rtype=UploadAlbumResponse)
	def uploadAlbum(self,album,**kw):
		res = UploadAlbumResponse()
		res.title = album.title
		res.track_sizes = []
		seq = 0
		for track in album.tracks:
			a=track.read()
			#f=open('/home/jakob/tmp/track%d.mp3' % seq,'wb')
			#f.write(a)
			#f.close()
			res.track_sizes += [len(a)]
			seq += 1
		return res

# -*- coding: utf-8 -*-

# This module can parse and create multipart-messages. The MultiPartReader
# is the parser that can read a multipart-message and stream the content
# into temporary files on the local filesystem.
# MultiPartWriter can create a multipart-message from strings or files on
# the local filesystem.
#
# Both classes read data in chunks and write their results to the filesystem
# in a stream-like manner. This way they will never take up more memory than
# is setup using the chunk_size argument.

import re,tempfile,os,time,hashlib
from ladon.compat import PORTABLE_BYTES, PORTABLE_STRING

rx_2linefeeds = re.compile(b'\n\n|\r\n\r\n',re.M)
rx_headers = re.compile(b'^([-_a-zA-Z0-9]+): (.*)$',re.M)

def upperkey(pair):
	return (pair[0].upper().replace(b'-',b'_'),pair[1].strip())

class MultiPartReader(object):
	def __init__(self,chunk_size,boundary,req,content_size=None):
		self.chunk_size = chunk_size
		self.content_size=content_size
		self.boundary = boundary
		rx_boundary = re.escape(boundary)
		self.rx_boundary_split = re.compile(b'--<b>\n|\n--<b>\n|\n--<b>--|--<b>\r\n|\r\n--<b>\r\n|\r\n--<b>--'.replace(b'<b>',boundary.replace('"','')) ,re.M)
		self.len_rest_chunk = len(boundary)+16
		self.rest_chunk = b''
		self.data = b''
		self.req = req
		self.attachments = {}
		self.attachments_by_id = {}
		self.eos = False
		self.interface_request = b''
		self.part_count = 0
		self.attachment_headers = b''
		self.attachment_headers_parsed = False
		self.tmpdir = None
		self.fd = None
		self.request_bytes_read = 0
		self.attachment_bytes_size = 0
		self.raw_dump_rest = False
		self.request_bytes_read = 0
		self.attachment_count = 0
		self.attachment_bytes_size = 0
		
	def write(self,data,eop=False):
		"""
		@param eop: End of parts
		"""
		global rx_2linefeeds,rx_headers
		if self.attachment_headers_parsed == False:
			self.attachment_headers += data
			m = rx_2linefeeds.search(self.attachment_headers)
			if m:
				data = self.attachment_headers[m.end():]
				self.attachment_headers = self.attachment_headers[:m.start()]
				self.attachment_headers_parsed = True
				
		if self.attachment_headers_parsed == True:
			self.attachment_bytes_size += len(data)
			if self.part_count==0:
				self.interface_request += data
				self.interface_request_headers = dict(map(upperkey,rx_headers.findall(self.attachment_headers)))
			else:
				os.write(self.fd,data)
			
			if eop==True:
				if self.fd != None:
					os.close(self.fd)
					headers_dict = dict(map(upperkey,rx_headers.findall(self.attachment_headers)))
					self.attachments[self.part_count-1]['size'] = self.attachment_bytes_size
					self.attachments[self.part_count-1]['headers'] = headers_dict
					if b'CONTENT_ID' in headers_dict:
						self.attachments_by_id[headers_dict[b'CONTENT_ID']] = self.attachments[self.part_count-1]
				
				if not self.eos:
					self.attachments[self.part_count] = {}
					self.fd,self.attachments[self.part_count]['path'] = tempfile.mkstemp('','content_',self.tmpdir)
					self.part_count += 1
				self.attachment_bytes_size = 0
				self.attachment_headers = b''
				self.attachment_headers_parsed = False
		
	def read_chunk(self):
		read_to_end = False
		read_size = self.chunk_size
		if self.content_size and self.content_size < self.request_bytes_read + read_size:
			read_size = self.content_size - self.request_bytes_read
		chunk = self.req.read(read_size)
		self.request_bytes_read += len(chunk)
		if chunk=='' or len(chunk)<self.chunk_size:
			read_to_end = True
		
		focus = self.rest_chunk+chunk
		parts = self.rx_boundary_split.split(focus)
		
		if len(parts)>1:
			self.data+=parts[0]
			self.write(self.data,True)
		
			for part in parts[1:-1]:
				self.write(part,True)
			self.data = b''
		if read_to_end == True:
			self.eos = True
		self.write(parts[-1:][0][:-self.len_rest_chunk])
		if self.eos:
			os.close(self.fd)
			os.unlink(self.attachments[self.part_count-1]['path'])
		self.rest_chunk = parts[-1:][0][-self.len_rest_chunk:]


class MultiPartWriter(object):
	def __init__(self,req,chunk_size=50000,boundary=None,header_encoding='iso-8859-1'):
		self.chunk_size = chunk_size
		self.header_encoding = header_encoding
		if not boundary:
			md5=hashlib.md5()
			md5.update(str(time.time()).encode(self.header_encoding))
			boundary = md5.hexdigest().encode(self.header_encoding)
		self.boundary = boundary
		self.req = req
	
	def add_attachment(self,data,content_type,content_id,headers={}):
		"""
		Add an attachment. Data must be binary meaning str for Python 2,
		bytes for Python 3 or a file-like object opened in binary mode.
		Content-type, content-id and strings in the headers dict can be
		strings but if they cannot be encoded to the encoding defined
		via the constructor an exception will be raised.
		Why? Because the result of this method is a binary object that
		will ultimately be inserted in a multipart message stream which
		is pure binary.
		"""
		if type(content_type)==PORTABLE_STRING:
			content_type = content_type.encode(self.header_encoding)
		if type(content_id)==PORTABLE_STRING:
			content_id = content_id.encode(self.header_encoding)
		self.req.write(b'--'+self.boundary+b'\n')
		self.req.write(b'Content-Type: '+content_type+b'\n')
		self.req.write(b'Content-ID: '+content_id+b'\n')
		for h_name,h_value in headers.items():
			try:
				if type(h_name)==PORTABLE_STRING:
					h_name = h_name.encode(self.header_encoding)
				if type(h_value)==PORTABLE_STRING:
					h_value = h_value.encode(self.header_encoding)
				self.req.write(h_name+b': '+h_value+b'\n')
			except:
				# ignore headers that can not be iso-8859-1 encoded or
				# otherwise fail to be added to the message part
				print('Failed header')
				pass
		self.req.write(b'\n')
		if hasattr(data,'read'):
			while 1:
				chunk = data.read(self.chunk_size)
				self.req.write(chunk)
				if chunk=='' or len(chunk)<self.chunk_size:
					break
			self.req.write(b'\n')
		elif type(data)==PORTABLE_BYTES:
			self.req.write(data)
			self.req.write(b'\n')

	def done(self):
		self.req.write(b'--'+self.boundary+b'--')


class AttachmentHandler(object):
	def __init__(self):
		self.cid_seq = 0
		self.attachments_by_cid = {}
		self.fs_attachments_map_cid = {}
	
	def get_next_cid(self):
		self.cid_seq += 1
		return 'ladon-attachment-%d' % self.cid_seq
		
	
	def add_attachment(self,attachment):
		if hasattr(attachment.bufferobj,'name'):
			# Could be a filesystem based attachment
			if os.path.exists(attachment.bufferobj.name):
				# Exists on filesystem
				fs_abspath = os.path.abspath(attachment.bufferobj.name)
				if fs_abspath not in self.fs_attachments_map_cid:
					# First encounter - no redundancy
					cid = self.get_next_cid()
					self.fs_attachments_map_cid[fs_abspath] = cid
					self.attachments_by_cid[cid] = attachment
					return 'cid:%s' % cid
				else:
					return 'cid:%s' % self.fs_attachments_map_cid[fs_abspath]
		else:
			cid = self.get_next_cid()
			self.attachments_by_cid[cid] = attachment
			return 'cid:%s' % cid


if __name__=='__main__':
	f=open('test.json','rb')
	mh=MultiPartReader(20000,b'493f4e46b6690ac551db9d306e7c5458',f)
	mh.read_chunk()
	while not mh.eos:
		mh.read_chunk()
	print(str(mh.interface_request_headers))
	print(str(mh.attachments_by_id))


	#f = open('test.json','wb')
	#mpw = MultiPartWriter(f)

	#a1=open('json-req','rb')
	#mpw.addAttachment(a1,'application/json, charset=iso-8859-1','dwezvfqrweverg0')
	#a1.close()

	#a1=open('/home/jakob/description','rb')
	#mpw.addAttachment(a1,'text/plain','dwezvfqrweverg1')
	#a1.close()

	#a1=open('/home/jakob/Billeder/trundfri.png','rb')
	#mpw.addAttachment(a1,'image/png','dwezvfqrweverg2')
	#a1.close()

	#mpw.done()
	#f.close()

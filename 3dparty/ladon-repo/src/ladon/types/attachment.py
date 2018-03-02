# -*- coding: utf-8 -*-
import os,re
from ladon.exceptions.dispatcher import NonExistingAttachment,InvalidAttachmentReference

class attachment(object):
	
	def __init__(self,bufferobj,bytesize=None,headers={},header_encoding='UTF-8'):
		"""
		attachment objects consist of a binary file-like buffer object and a header
		dict. The 
		"""
		from ladon.compat import PORTABLE_BYTES
		self.headers = {}
		self.size = bytesize
		for k,v in headers.items():
			if type(k)==PORTABLE_BYTES:
				k = k.decode(header_encoding)
			if type(v)==PORTABLE_BYTES:
				v = v.decode(header_encoding)
			self.headers[k] = v
		self.bufferobj = bufferobj
		self.read = self.bufferobj.read
		if hasattr(self.bufferobj,'readline'):
			self.readline = self.bufferobj.readline
		if hasattr(self.bufferobj,'readlines'):
			self.readlines = self.bufferobj.readlines
		if hasattr(self.bufferobj,'xreadlines'):
			self.xreadlines = self.bufferobj.xreadlines
		if hasattr(self.bufferobj,'seek'):
			self.seek = self.bufferobj.seek
		if hasattr(self.bufferobj,'readinto'):
			self.readinto = self.bufferobj.readinto
		if hasattr(self.bufferobj,'flush'):
			self.flush = self.bufferobj.flush
		if hasattr(self.bufferobj,'closed'):
			self.closed = self.bufferobj.closed
		self.close = self.bufferobj.close

	def __del__(self):
		if self.bufferobj:
			self.bufferobj.close()

	def header(self,name):
		if name in self.headers:
			return self.headers[name]
		else:
			return None
	
	def headers(self):
		return self.headers


def extract_attachment_reference(a_reference,export_dict,req_encoding,ifname='',sname=''):
	rx_cid = re.compile('^cid:(.+)$',re.I)
	rx_cidx = re.compile('^cidx:(\d+)$',re.I)

	m = None
	for rx in [rx_cid,rx_cidx]:
		m = rx.match(a_reference)
		if m and rx==rx_cid:
			cid = m.groups()[0].encode(req_encoding)
			if cid and 'attachments_by_id' in export_dict and cid in export_dict['attachments_by_id']:
				attachment_info = export_dict['attachments_by_id'][cid]
				return attachment(open(attachment_info['path'],'rb'),attachment_info['size'],attachment_info['headers'],req_encoding)
			else:
				raise NonExistingAttachment(ifname,sname,'Attachment reference %s is not part of the request' % cid)
			break
		if m and rx==rx_cidx:
			cidx = int(m.groups()[0].encode(req_encoding))
			if 'attachments' in export_dict and cidx in export_dict['attachments']:
				attachment_info = export_dict['attachments'][cidx]
				return attachment(open(attachment_info['path'],'rb'),attachment_info['size'],attachment_info['headers'],req_encoding)
			else:
				raise NonExistingAttachment(ifname,sname,'Attachment with index:%d is not part of the request' % cidx)
			break
	if not m:
		raise InvalidAttachmentReference(ifname,sname,'Attachment reference %s has invalid format, must be cid:<ref> or cidx:<index>' % a_reference)


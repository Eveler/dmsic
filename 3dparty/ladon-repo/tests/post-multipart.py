import httplib,urlparse,urllib


class RequestPoster(object):
	def __init__(self,url):
		self.valid_url = True
		parseres = urlparse.urlparse(url)
		self.scheme = parseres.scheme
		if self.scheme.lower()=="https":
			self.port = 443
		elif self.scheme.lower()=="http":
			self.port = 80
		else:
			self.valid_url = False
		self.hostname,custom_port = urllib.splitport(parseres.netloc)
		if str(custom_port).isdigit():
			self.port = int(custom_port)
		self.path = parseres.path

	def post_request(self,data,extra_path="jsonwsp"):
		headers = {
			"Content-Type": "multipart/related; boundary=493f4e46b6690ac551db9d306e7c5458",
			"Accept": "text/html,application/xhtml+xml,application/xml,multipart/related;q=0.9,*/*;q=0.8" }
		if self.scheme.lower()=='https':
			conn = httplib.HTTPSConnection(self.hostname,self.port)
		else:
			conn = httplib.HTTPConnection(self.hostname,self.port)
		req_path = self.path + '/' + extra_path
		conn.request("POST", req_path, data, headers)
		response = conn.getresponse()
		status, reason = response.status, response.reason
		resdata = response.read()
		conn.close()
		return status,reason,resdata


rp = RequestPoster('http://localhost:2376/AttachmentTestService')
#print rp.post_request(open('data/attachmenttests/multipart.json').read())
print(rp.post_request(open('test.json').read())[2])

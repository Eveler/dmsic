# -*- coding: utf-8 -*-

from ladon.clients.jsonwsp import JSONWSPClient
import pprint,os
from os.path import join,dirname,abspath

base_url = 'http://localhost:8080'

files_dir = join(dirname(abspath(__file__)),'files')
download_dir = join(dirname(abspath(__file__)),'download')

for d in [files_dir,download_dir]:
  if not os.path.exists(d):
    os.mkdir(d)

def print_result(jsonwsp_resp):
	if jsonwsp_resp.status == 200:
		if 'result' in jsonwsp_resp.response_dict:
			pprint.pprint(jsonwsp_resp.response_dict['result'],indent=2)
		else:
			pprint.pprint(jsonwsp_resp.response_dict)
	else:
		print("A problem occured while communicating with the service:\n")
		print(jsonwsp_resp.response_body)

def testCalculator():

	global base_url
	print("\n\nTesting Calculator:\n")
	# Load the Calculator description
	
	calc_client = JSONWSPClient(base_url + '/Calculator/jsonwsp/description')

	# Add the numbers 23 and 45
	jsonwsp_resp = calc_client.add(a=23,b=45)
	print_result(jsonwsp_resp)


def testAlbumService():

	print("\n\nTesting AlbumService:\n")
	# Load the AlbumService description
	album_client = JSONWSPClient(base_url + '/AlbumService/jsonwsp/description')

	# Fetch albums containing the substring "Zoo" in the album title
	jsonwsp_resp = album_client.listAlbums(search_frase='Bowie')
	print_result(jsonwsp_resp)

	# Fetch all bands containing the substring "Bowie" in the band name
	jsonwsp_resp = album_client.listBands(search_frase='Bowie')
	print_result(jsonwsp_resp)


def testTransferService():
	global files_dir, download_dir

	print("\n\nTesting TransferService:\n")
	# Load the TransferService description
	transfer_client = JSONWSPClient(base_url + '/TransferService/jsonwsp/description')

	# File list for the upload() call
	file_list = []
	# list of file names fot the download() call
	name_list = []
	
	# Get a list of files in the "files" folder
	files = os.listdir(files_dir)
	for f in files:
		fpath = os.path.join(files_dir,f)
		# Check if the entry is a file
		if os.path.isfile(fpath):
			# Add the file as a TransferService.File object (for the upload() call)
			file_list += [ {
				'data': open(fpath,'rb'), # Attach the file using an open file-handle
				'name': f                 # The file name
			} ]
			
			# Add the file name to the list of file names (for the download() call)
			name_list += [f]
	
	# Upload multiple files (all files found in the "files" directory) in one request
	jsonwsp_resp = transfer_client.upload(incomming=file_list)
	print_result(jsonwsp_resp)

	# Download all the files we just uploaded in one request
	jsonwsp_resp = transfer_client.download(names=name_list)
	print_result(jsonwsp_resp)

	# The attachments are referenced as open file-handles in the response object
	# read their content and save it as files in the "download" folder.
	if jsonwsp_resp.status==200:
		for f in jsonwsp_resp.response_dict['result']:
			print(f)
			fp = open(os.path.join(download_dir,f['name']),'wb')
			fp.write(f['data'].read())
			fp.close()


if __name__=='__main__':
	testCalculator()
	testAlbumService()
	testTransferService()

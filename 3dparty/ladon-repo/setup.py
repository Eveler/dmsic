#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys,os

readme = changes = ''
if os.path.exists('README.rst'):
	readme = open('README.rst').read()
if os.path.exists('CHANGES.rst'):
	changes = open('CHANGES.rst').read()

import imp
m=imp.load_source('init','src/ladon/__init__.py')
VERSION = '%(major)s.%(minor)s.%(micro)s' % m._version_info

SHORT_DESC = "Serve your python methods to several web service interfaces at once, including JSON-WSP, SOAP and JSON-RPC."
PACKAGES = find_packages('src')

install_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(install_dir,'scripts')

ladon_command = 'ladon-%d.%d-ctl%s' % (sys.version_info.major,sys.version_info.minor,'.py' if sys.platform.find('win')==0 else '')
scriptfiles = [os.path.join('scripts',ladon_command),os.path.join('scripts','ladon-ctl')]
f_ladon_temp = open(os.path.join(scripts_dir,'ladon-ctl'))
f_ladon_cmd = open(os.path.join(scripts_dir,ladon_command),'w')
f_ladon_cmd.write(f_ladon_temp.read().replace('<INTERPRETER>',sys.executable))
f_ladon_cmd.close()
f_ladon_temp.close()


def walk_dir(dirname):
	files = []
	def detect_svn(fname):
		return fname.find('.svn')==-1
	for f in filter(detect_svn ,map(lambda fname: os.path.join(dirname,fname),os.listdir(dirname))):
		if os.path.isdir(f):
			continue
		files += [f]
	return files

setup(
	name='ladon',
	packages=PACKAGES,
	package_dir={'':'src'},
	version=VERSION,
	description=SHORT_DESC,
	long_description='\n\n'.join([readme, changes]),
	classifiers=[
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Operating System :: OS Independent',
		'Natural Language :: English',
		'Intended Audience :: Developers',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',       
	],
	keywords= ['ladonize', 'soap', 'json', 'shell', 'rpc', 'wsgi'],
	author='Jakob Simon-Gaarde',
	author_email='jakob@simon-gaarde.dk',
	maintainer = 'Jakob Simon-Gaarde',
	maintainer_email = 'jakob@simon-gaarde.dk',
	url='http://ladonize.org',
	install_requires=['jinja2','sphinx','sphinx_bootstrap_theme','chardet'],
	requires=['jinja2','sphinx','sphinx_bootstrap_theme','chardet'],
	provides=['ladon'],
	license='LGPL3',
	scripts=scriptfiles,
	include_package_data=True,
	zip_safe=False
)

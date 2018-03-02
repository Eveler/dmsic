import os

_version_info = {
	'major': 0,
	'minor': 9,
	'micro': 39
}

__version__ = "%(major)s.%(minor)s.%(micro)s" % _version_info

def package_root(*subpath):
	root_parts = [__file__,'..']
	if subpath:
		root_parts += list(subpath)
	return os.path.abspath(os.path.join(*root_parts))

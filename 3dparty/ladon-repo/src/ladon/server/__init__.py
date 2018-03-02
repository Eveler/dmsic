# -*- coding: utf-8 -*-

NO_LOGGING = 0
LOG_REQUEST_ACCESS = 1
LOG_REQUEST_DICT = 2
LOG_RESPONSE_DICT = 4
LOG_EXECUTION_TIME = 8
LOG_JSON_FORMAT = 16

content_types = {
	'js': {
		'Content-Type': 'application/javascript',
		'Content-Encoding': 'gzip'
	},
	'html': {
		'Content-Type': 'text/html',
		'Content-Encoding': 'gzip'
	},
	'css': {
		'Content-Type': 'text/css',
		'Content-Encoding': 'gzip'
	},
	'svg': {
		'Content-Type': 'image/svg+xml',
		'Content-Encoding': 'gzip'
	},
	'png': {
		'Content-Type': 'image/png'
	},
	'gif': {
		'Content-Type': 'image/gif'
	},
	'jpg': {
		'Content-Type': 'image/jpeg'
	},
	'bmp': {
		'Content-Type': 'image/bmp'
	},
	'ico': {
		'Content-Type': 'image/x-icon'
	},
	'dmg': {
		'Content-Type': 'application/x-apple-diskimage'
	}
}

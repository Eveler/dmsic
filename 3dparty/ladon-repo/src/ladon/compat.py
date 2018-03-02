import sys
from ladon.types.attachment import attachment

if sys.version_info[0]==2:
	import StringIO,cStringIO
	StringIO = StringIO.StringIO
	BytesIO = cStringIO.StringIO
	PORTABLE_BYTES = str
	PORTABLE_STRING = unicode
	pytype_support = [int,long,str,unicode,bool,float]
	
	safe_conversions = {
		int: [int,long,str,unicode,float],
		long: [long,int,str,unicode], # Python 2 automatically turns int into long therefore this is regarded as a safe conversion
		str: [str,unicode],
		unicode: [unicode,str],
		bool: [bool,int,long,str,unicode,bool,float],
		float: [float,str,unicode]
	}
	
	PORTABLE_STRING_TYPES = [unicode,str]
	
	type_to_xsd = {
		int: 'long',
		long: 'long',
		str: 'string',
		unicode: 'string',
		bool: 'boolean',
		float: 'decimal',
		attachment: 'binary'
	}

	type_to_jsontype = {
		int: 'number',
		long: 'number',
		str: 'string',
		unicode: 'string',
		bool: 'boolean',
		float: 'float',
		attachment: 'attachment'
	}

elif sys.version_info[0]>=3:
	import io
	StringIO = io.StringIO
	BytesIO = io.BytesIO
	
	PORTABLE_BYTES = bytes
	PORTABLE_STRING = str
	pytype_support = [int,bytes,str,bool,float]

	safe_conversions = {
		int: [int,bytes,str],
		bytes: [bytes,str],
		str: [str,bytes],
		bool: [bool,int,bytes,str,bool,float],
		float: [float,bytes,str]
	}
	
	PORTABLE_STRING_TYPES = [str,bytes]
	
	type_to_xsd = {
		int: 'long',
		bytes: 'string',
		str: 'string',
		bool: 'boolean',
		float: 'decimal',
		attachment: 'binary'
	}

	type_to_jsontype = {
		int: 'number',
		bytes: 'string',
		str: 'string',
		bool: 'boolean',
		float: 'float',
		attachment: 'attachment'
	}

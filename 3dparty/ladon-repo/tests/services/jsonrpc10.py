from ladon.ladonizer import ladonize
from ladon.compat import PORTABLE_BYTES,PORTABLE_STRING
import binascii
import sys

class JsonPrc10Service(object):
    @ladonize(rtype=PORTABLE_STRING)
    def return_string(self):
        if sys.version_info[0]>=3:
            return 'Yo!!!'
        return PORTABLE_STRING('Yo!!!','utf-8')
    
    @ladonize(rtype=int)
    def return_int(self):
        return 11
    
    @ladonize(rtype=float)
    def return_float(self):
        return 11.11
    
    @ladonize(rtype=bool)
    def return_bool(self):
        return True
    
    @ladonize(rtype=PORTABLE_BYTES)
    def return_bytes(self):
        if sys.version_info[0]>=3:
            return PORTABLE_BYTES('Yo!!!','utf-8')
        return 'Yo!!!'
    
    @ladonize(PORTABLE_STRING, rtype=PORTABLE_STRING)
    def passback_string(self,arg):
        return arg
    
    @ladonize(int,rtype=int)
    def passback_int(self,arg):
        return arg
    
    @ladonize(float,rtype=float)
    def passback_float(self,arg):
        return arg
    
    @ladonize(bool,rtype=bool)
    def passback_bool(self,arg):
        return arg
    
    @ladonize(PORTABLE_BYTES,rtype=PORTABLE_BYTES)
    def passback_bytes(self,arg):
        return arg
    
    @ladonize(int,float,PORTABLE_STRING,rtype=bool)
    def params(self,arg0,arg1,arg2):
        return True
        
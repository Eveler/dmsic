# -*- coding: utf-8 -*-
from ladon.ladonizer import ladonize
from ladon.types.ladontype import LadonType
from ladon.compat import PORTABLE_STRING

class Grocery(LadonType):
	item_name = PORTABLE_STRING
	price = float

class Purchase(LadonType):
	grocery = Grocery
	quantity = int

class GroceryList(LadonType):
	purchases = [ Purchase ]

class ShopService(object):
	
	@ladonize(GroceryList,rtype=int)
	def addToBasket(self,glist):
		return 1

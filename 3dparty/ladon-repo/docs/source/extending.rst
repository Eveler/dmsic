Extending Ladon with new interface protocols
============================================

.. autoclass:: ladon.interfaces.base.BaseInterface
   :members: __init__

It is recommended that you study ladon.interfaces.jsonwsp to learn howto extend Ladon with more protocols.

Adding the interface
--------------------
Currently you have to add an import statement in the bottom of ladon/interfaces/__init__.py to add your
protocol to Ladon. This is a temporary solution.

Like this::
	
	import ladon.interfaces.soap
	import ladon.interfaces.jsonwsp
	# My CORBA implementation
	import ladon.interfaces.corba

.. toctree::
   :maxdepth: 2

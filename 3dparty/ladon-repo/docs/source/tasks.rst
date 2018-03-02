Ladon Tasks
===========

Description
-----------
Ladon tasks are ladonzed methods that are executed in the background - also called task-type methods. The Ladon framework takes
care of almost everything so you as a service developer can concentrate on the code. There is essentially no difference in making
a "normal" ladonized method and a task-type ladonized method. The only thing you as a developer have to think of is protecting
access to non-local objects. So if you are keeping state between several method requests in a global object you will need to
use some sort of locking mechanism.

Example
-------
Let's say for instance you are implementing a web service interface for a virtualization center, then one of your methods might
look like this::

	class InstanceService(object):

		@ladonize(PORTABLE_STRING, PORTABLE_STRING, rtype=InstanceInformation)
		def cloneInstance(self,instance_id,new_instance_name, **kw):
			response = InstanceInformation()
			...
			...
			return response

In this example we imagine that the method **cloneInstance** will create a new instance with the name **new_instance_name** as an
exact copy of the existing instance identified by **instance_id**. The result of the clone operation is returned in the *LadonType*
**InstanceInformation**. It is not hard to imagine that such an operation will take time having tasks like:
	- Configuring and creating a new virtual destination instance
	- Copying all disk images from the source instance
	- Maybe starting it up as an option

So let's say that this operation takes minutes. If you expose the method like above the requesting connection will block
for just as long time waiting for the response to come back. Also the back-end has no way of reporting back to the end-user
how far into the operation it has progressed.

To effectively solve all of the above problems expose the method as a Ladon task instead::

	class InstanceService(object):

		@ladonize(PORTABLE_STRING, PORTABLE_STRING, rtype=InstanceInformation, tasktype=True)
		def cloneInstance(self,instance_id,new_instance_name, **kw):
			response = InstanceInformation()
			...
			kw['update_progress'](0.3)
			...
			return response

The only extra code you will need to add in the task-type implementation is progress updating.

What is the effect for the end-user
-----------------------------------
So how does task-types really affect your service? Well in pratice what we have done is created a server-side asynchronious method
which starts the method code, but instead of returning the a **InstanceInformation** *LadonType* response as was defined it returns
a **task_id** immediately in a LadonType called **TaskInfoResponse**::

	class TaskInfoResponse(LadonType):
		task_id = {
			'type': int,
			'doc': u'unique integer identifying the task to that has been created'
		}

So this will start the task. To continuously monitor the progress from the user-end just call the task's corresponding
<method-name>_progress() method which returns a LadonType called **TaskProgressResponse**::

	class TaskProgressResponse(LadonType):
		task_id = {
			'type': int,
			'doc': u'unique integer identifying the task to that has been probed'
		}
		progress = {
			'type': float,
			'doc': u'Floating point value between 0 and 1 denoting the progress in percent'
		}
		duration = {
			'type': float,
			'doc': u'Floating point value that informs how long time in seconds the task as run'
		}
		starttime = {
			'type': float,
			'doc': u'The start time in seconds since the epoch as a floating point number'
		}

When the task has finished running the result can be retreived using the task's <method-name>_result() method. It returns the type
you originally defined your task-method to return using the ladonize decorator's rtype keyword.

To summerize let's see what the effect of the above example would be for the end-user.

As already explained the method you originally defined and exposed has been split into 3 exposed methods. So the method from the
example **cloneInstance** will expand to the following methods at the user-end:
	- cloneInstance(self, instance_id, new_instance_name)
		- returning a **TaskInfoResponse**
	- cloneInstance_progress(self, task_id)
		- returning a **TaskProgressResponse**
	- cloneInstance_result(self, taskid)
		- returning the return type defined in the ladonize decorator: **InstanceInformation**

Updating a task's progress
--------------------------
Progress values in Ladon are defined as float values between 0 and 1 denoting the progress in percent.

Once a task has been started it must update it's own progress continuously. Needless to say the more frequently you as a service
developer update the progress the better the resolution and experience the end-user will get.

Ladon will initially set a new task's progress to 0.0 and also set it to 1.0 once the task has ended. So even if you somehow can't
update the progress the task will work as it should.

The function for updating a task's progress is passed to the method via the keyword argument **update_progress**. It takes a float
between 0 and 1 as argument. Values less than 0 and larger than 1 will be converted to 0 and 1 respectively.

Here is a full Ladon task example using progress update::

	from ladon.compat import PORTABLE_STRING
	from ladon.ladonizer import ladonize
	import time

	class TaskService(object):

		@ladonize(PORTABLE_STRING, int, rtype=int, tasktype=True)
		def taskExample(self,session_id,counter,**kw):
			set_progress = kw['update_progress']
			repeat = 60.0
			for i in range(int(repeat)):
				time.sleep(.5)
				set_progress(float(i+1.0)/repeat)
			return counter

Cave-eats (version 0.9.8)
-------------------------
	- Uses the threading module meaning that **GIL** is in play
	- Task state is kept in global python variables and therefore do not work cross-host nor cross-process

In many use-cases these cave-eats are not a problem. Ie. if your task spawns a new synchronious process
like a system-call you will not be having problems with *GIL* and the current implementation will work as
long as your application stays within the same process.

The good thing about the current solution is that it works out-of-the-box without introducing thirdparty
state-keeping services. It should also be noted that if you are using ie. mod-wsgi on apache2 it is
possible to control process groups for specific Ladon services, so you can configure your apache server
to use only one process for your services containing task type Ladon methods, and multiple procesesses for
your other services that do not need to keep state like Ladon tasks::

	<VirtualHost *:80>
	
		ServerName my-site.com
		ServerAdmin webmaster@localhost

		WSGIDaemonProcess my-site.com user=jakob group=www-data threads=25
		WSGIProcessGroup my-site.com

		WSGIScriptAlias / /srv/my-site-service/handler.py

		<Directory /srv/www/cal.limbosoft.com/>
			Require all granted
		</Directory>

	</VirtualHost>

In the above mod-wsgi example, all requests are kept in the same process with up to 25 threads.
	
Solution (version 1.0.0)
------------------------
The solution for the cave-eats mentioned will be the option to configure socket-based state caching like
memcached or redis. If using the thirdparty state caching option Ladon will shift over to using the
multiprocessing module for task execution. This solution should solve both cave-eats and will be when
Ladon turns into 1.0.0.

The current implementation will probably stay in Ladon because it is very easy to use and requires no
extra configuration other than the keyword in your ladonize decorator

.. toctree::
   :maxdepth: 2
 

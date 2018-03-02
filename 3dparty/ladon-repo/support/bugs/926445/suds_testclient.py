from suds.client import Client

c=Client('http://localhost:8888/CustomerService/soap/description',cache=None)

rep = c.factory.create('Report')

rep.customer= None
rep.rid='id389423'
rep.summary=u'Anonymous customer filing a nice report.'
rep.nulllist = None

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

res = c.service.addReport(rep)
print("\nResult:")
print(res)


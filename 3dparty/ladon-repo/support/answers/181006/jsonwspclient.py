from ladon.clients.jsonwsp import JSONWSPClient
import pprint

cli = JSONWSPClient('http://127.0.0.1:8888/TestService/jsonwsp/description')

r = cli.createServerFault()
pprint.pprint(r.response_dict)

r = cli.blameClientFault()
pprint.pprint(r.response_dict)

r = cli.unmanagedFault(anumber=1)
pprint.pprint(r.response_dict)

r = cli.unmanagedFault(anumber='hfiuwef')
pprint.pprint(r.response_dict)



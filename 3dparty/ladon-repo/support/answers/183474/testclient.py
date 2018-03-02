from suds.client import Client

cli = Client('http://localhost:8888/KVService/soap/description')

kv = cli.factory.create('KeyValue')
kv.key = u'Test Key'
kv.value = u'Test Value'

print cli.service.testKeyValues([kv])

from cabby import create_client
from stix.core import STIXPackage
import json
from lxml import etree

def print_collection_content_bindings(collection):
    cbs = collection.content_bindings
    print('Content bindings len = %s' % (len(cbs)))
    for cb in cbs:
        print('id %s, subtypes %s' % (cb.id, cb.subtypes))

def print_collection_subscription_methods(collection):
    sms = collection.subscription_methods
    print('Subscription methods len = %s' % (len(sms)))
    for sm in sms:
        print('protocol %s, address %s, message_bindings %s' % 
              (sm.protocol, sm.address, sm.message_bindings))


def run_taxii():
    client = create_client(
        'otx.alienvault.com',
        use_https=True,
        discovery_path='/taxii/discovery')

    collection_services = []
    for service in client.discover_services():
        print('Service type={s.type}, available={s.available}, '
              'address={s.address}'.format(s=service))
        
        if service.type == 'COLLECTION_MANAGEMENT' and service.available:
            collection_services.append(service.address)
    
    if not collection_services:
        print('No available collection services found')
        return
    
    collections = client.get_collections(uri=collection_services[0])
    print('Found %s collections' % (len(collections)))
    if not collections:
        return
    
    collection = collections[0]
    print('collection name {c.name}, type {c.type}, '
          'available {c.available}, volume {c.volume}'.format(
              c=collection))
    print_collection_content_bindings(collection)
    print_collection_subscription_methods(collection)
    
#     limit_blocks = 1
#     c = 0
#     file_name = 'alien-vault-max-%s-blocks.xml' % limit_blocks
#     with open(file_name, 'wb') as fout:
#         for block in client.poll(collection_name=collection.name):
#             fout.write(block.content)
#             c += 1
#             if c == limit_blocks:
#                 break
#              
#     print('%s blocks written to %s' % (c, file_name))

def run_stix(file_name):
#     with open(file_name) as fin:
#         e = etree.fromstring(fin.read())
#         print(type(e))
        
    # gives error with stix 1.1.1.12 when file with 1 block is provided
    stix_package = STIXPackage.from_xml(file_name)
    
    dict_stix_package = stix_package.to_dict()
    for k, v in dict_stix_package.items():
        print('%s\n%s' % (k, json.dumps(v, indent=2)))

if __name__ == '__main__':
    #run_taxii()
    run_stix('alien-vault-max-1-blocks.xml')

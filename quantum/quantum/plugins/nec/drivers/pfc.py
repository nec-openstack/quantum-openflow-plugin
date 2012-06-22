# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import logging

from quantum.plugins.nec.tools.client import Client

tenants_path = "/tenants"
tenant_path = "/tenants/%s"
networks_path = "/tenants/%s/networks"
network_path = "/tenants/%s/networks/%s"
ports_path = "/tenants/%s/networks/%s/ports"
port_path = "/tenants/%s/networks/%s/ports/%s"

LOG = logging.getLogger(__name__)


class PFCDriver(object):

    def __init__(self, host='localhost', port=8888):
        self.client = Client(host=host, port=port, format='json')

    @classmethod
    def filter_supported(cls):
        return False

    def create_tenant(self, tenant_id):
        body = {'description': tenant_id}
        res = self.client.post(tenants_path, body=body)
        ofn_tenant_id = res['id']
        return ofn_tenant_id

    def delete_tenant(self, ofn_tenant_id):
        path = tenant_path % ofn_tenant_id
        return self.client.delete(path)

    def create_network(self, ofn_tenant_id, network_id, network_name):
        path = networks_path % ofn_tenant_id
        body = {'description': network_name}
        res = self.client.post(path, body=body)
        ofn_network_id = res['id']
        return ofn_network_id

    def delete_network(self, ofn_tenant_id, ofn_network_id):
        path = network_path % (ofn_tenant_id, ofn_network_id)
        return self.client.delete(path)

    def rename_network(self, ofn_tenant_id, ofn_network_id, new_network_name):
        path = network_path % (ofn_tenant_id, ofn_network_id)
        body = {'description': new_network_name}
        return self.client.put(path, body=body)

    def create_port(self, ofn_tenant_id, ofn_network_id, port_id, vifinfo):
        path = ports_path % (ofn_tenant_id, ofn_network_id)
        body = {'datapath_id': vifinfo.datapath_id,
                'port': str(vifinfo.port_no),
                'vid': str(vifinfo.vlan_id)}
        res = self.client.post(path, body=body)
        ofn_port_id = res['id']
        return ofn_port_id

    def delete_port(self, ofn_tenant_id, ofn_network_id, ofn_port_id):
        path = port_path % (ofn_tenant_id, ofn_network_id, ofn_port_id)
        return self.client.delete(path)

# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import logging
from webob import exc

from quantum.plugins.nec.tools.client import Client

LOG = logging.getLogger(__name__)


class TremaNetworkDriver(object):
    networks_path = "/networks"
    network_path = "/networks/%s"

    def __init__(self, host='localhost', port=8888):
        self.client = Client(host=host, port=port, format='json')

    def create_tenant(self, tenant_id):
        return tenant_id

    def delete_tenant(self, ofn_tenant_id):
        pass

    def create_network(self, ofn_tenant_id, network_id, network_name):
        body = {'id': network_id, 'description': network_name}
        self.client.post(self.networks_path, body=body)
        return network_id

    def delete_network(self, ofn_tenant_id, ofn_network_id):
        path = self.network_path % ofn_network_id
        return self.client.delete(path)

    def rename_network(self, ofn_tenant_id, ofn_network_id, new_network_name):
        path = self.network_path % ofn_network_id
        body = {'description': new_network_name}
        return self.client.put(path, body=body)


class TremaFilterDriver(object):
    filters_path = "/filters"
    filter_path = "/filters/%s"

    @classmethod
    def filter_supported(cls):
        return True

    def create_filter(self, ofn_tenant_id, ofn_network_id, filter,
                      vifinfo=None):
        if filter.action.upper() in "ACCEPT":
            ofn_action = "ALLOW"
        elif filter.action.upper() in "DROP":
            ofn_action = "DENY"

        body = {'priority': filter.priority,
                'slice': ofn_network_id,
                'action': ofn_action}
        ofp_wildcards = ["dl_vlan", "dl_vlan_pcp", "nw_tos"]

        if vifinfo:
            body['in_datapath_id'] = vifinfo.datapath_id
            body['in_port'] = vifinfo.port_no
        else:
            body['wildcards'] = "in_datapath_id"
            ofp_wildcards.append("in_port")

        if filter.src_mac:
            body['dl_src'] = filter.src_mac
        else:
            ofp_wildcards.append("dl_src")

        if filter.dst_mac:
            body['dl_dst'] = filter.dst_mac
        else:
            ofp_wildcards.append("dl_dst")

        if filter.src_cidr:
            body['nw_src'] = filter.src_cidr
        else:
            ofp_wildcards.append("nw_src:32")

        if filter.dst_cidr:
            body['nw_dst'] = filter.dst_cidr
        else:
            ofp_wildcards.append("nw_dst:32")

        if filter.protocol:
            if filter.protocol.upper() in "ICMP":
                body['dl_type'] = "0x800"
                body['nw_proto'] = hex(1)
            elif filter.protocol.upper() in "TCP":
                body['dl_type'] = "0x800"
                body['nw_proto'] = hex(6)
            elif filter.protocol.upper() in "UDP":
                body['dl_type'] = "0x800"
                body['nw_proto'] = hex(17)
            elif filter.protocol.upper() in "ARP":
                body['dl_type'] = "0x806"
                ofp_wildcards.append("nw_proto")
            else:
                msg = "unknown protocol %s." % filter.protocol
                LOG.error("ofn_create_filter(): %s" % msg)
                raise exc.HTTPInternalServerError(msg)
        else:
            ofp_wildcards.append("dl_type")
            ofp_wildcards.append("nw_proto")

        if filter.src_port:
            body['tp_src'] = hex(filter.src_port)
        else:
            ofp_wildcards.append("tp_src")

        if filter.dst_port:
            body['tp_dst'] = hex(filter.dst_port)
        else:
            ofp_wildcards.append("tp_dst")

        ofn_filter_id = filter.uuid
        body['id'] = ofn_filter_id

        body['ofp_wildcards'] = ','.join(ofp_wildcards)

        self.client.post(self.filters_path, body=body)
        return ofn_filter_id

    def delete_filter(self, ofn_tenant_id, ofn_network_id, ofn_filter_id):
        path = self.filter_path % ofn_filter_id
        return self.client.delete(path)

# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import logging
from webob import exc

from quantum.plugins.nec.drivers.trema import (TremaNetworkDriver,
                                               TremaFilterDriver)

LOG = logging.getLogger(__name__)


class TremaPortBaseDriver(TremaNetworkDriver, TremaFilterDriver):
    ports_path = "/networks/%s/ports"
    port_path = "/networks/%s/ports/%s"

    def create_port(self, ofn_tenant_id, ofn_network_id, port_id, vifinfo):
        ofn_port_id = port_id
        path = self.ports_path % ofn_network_id
        body = {'id': ofn_port_id,
                'datapath_id': vifinfo.datapath_id,
                'port': str(vifinfo.port_no),
                'vid': str(vifinfo.vlan_id)}
        self.client.post(path, body=body)
        return ofn_port_id

    def delete_port(self, ofn_tenant_id, ofn_network_id, ofn_port_id):
        path = self.port_path % (ofn_network_id, ofn_port_id)
        return self.client.delete(path)

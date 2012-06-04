# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import logging
from webob import exc

from quantum.plugins.nec.drivers.trema import (TremaNetworkDriver,
                                               TremaFilterDriver)

LOG = logging.getLogger(__name__)


class TremaPortMACBaseDriver(TremaNetworkDriver, TremaFilterDriver):
    ports_path = "/networks/%s/ports"
    port_path = "/networks/%s/ports/%s"
    attachments_path = "/networks/%s/ports/%s/attachments"
    attachment_path = "/networks/%s/ports/%s/attachments/%s"

    def create_port(self, ofn_tenant_id, ofn_network_id, port_id, vifinfo):
        #NOTE: This Driver create slices with Port-MAC Based bindings on Trema
        #      Sliceable.  It's REST API requires Port Based binding before you
        #      define Port-MAC Based binding.
        ofn_port_id = port_id
        dummy_port_id = "dummy-%s" % port_id

        path = self.ports_path % ofn_network_id
        body = {'id': dummy_port_id,
                'datapath_id': vifinfo.datapath_id,
                'port': str(vifinfo.port_no),
                'vid': str(vifinfo.vlan_id)}
        self.client.post(path, body=body)

        path = self.attachments_path % (ofn_network_id, dummy_port_id)
        body = {'id': ofn_port_id, 'mac': vifinfo.mac}
        self.client.post(path, body=body)

        path = self.port_path % (ofn_network_id, dummy_port_id)
        self.client.delete(path)

        return ofn_port_id

    def delete_port(self, ofn_tenant_id, ofn_network_id, ofn_port_id):
        dummy_port_id = "dummy-%s" % ofn_port_id

        path = self.attachment_path % (ofn_network_id, dummy_port_id,
                                       ofn_port_id)
        return self.client.delete(path)

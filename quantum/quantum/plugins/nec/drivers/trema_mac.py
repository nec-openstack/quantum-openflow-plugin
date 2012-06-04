# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import logging

from quantum.plugins.nec.drivers.trema import TremaNetworkDriver

LOG = logging.getLogger(__name__)


class TremaMACBaseDriver(TremaNetworkDriver):
    attachments_path = "/networks/%s/attachments"
    attachment_path = "/networks/%s/attachments/%s"

    @classmethod
    def filter_supported(cls):
        return False

    def create_port(self, ofn_tenant_id, ofn_network_id, port_id, vifinfo):
        ofn_port_id = port_id
        path = self.attachments_path % ofn_network_id
        body = {'id': ofn_port_id, 'mac': vifinfo.mac}
        self.client.post(path, body=body)
        return ofn_port_id

    def delete_port(self, ofn_tenant_id, ofn_network_id, ofn_port_id):
        path = self.attachment_path % (ofn_network_id, ofn_port_id)
        return self.client.delete(path)

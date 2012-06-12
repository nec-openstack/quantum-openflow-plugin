# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

from nova import flags
from nova import log as logging
from nova.openstack.common import cfg
from nova.network.linux_net import LinuxOVSInterfaceDriver

import quantum.plugins.nec.nova.vifinfo_client as client

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS


class LinuxOVSVIFINFOInterfaceDriver(LinuxOVSInterfaceDriver):
    """
    Configure nova.conf as follows:
        linuxnet_ovs_integration_bridge=br-int
        linuxnet_interface_driver=\
            quantum.plugins.nec.nova.linux_net.LinuxOVSVIFINFOInterfaceDriver
    """

    def plug(self, network, mac_address, gateway=True):
        dev = super(LinuxOVSVIFINFOInterfaceDriver, self).plug(network,
                                                               mac_address,
                                                               gateway)
        interface_id = dev
        bridge = FLAGS.linuxnet_ovs_integration_bridge
        client.update_vifinfo(interface_id, bridge, dev, mac_address)
        return dev

    def unplug(self, network):
        interface_id = self.get_dev(network)
        client.delete_vifinfo(interface_id)
        return super(LinuxOVSVIFINFOInterfaceDriver, self).unplug(network)

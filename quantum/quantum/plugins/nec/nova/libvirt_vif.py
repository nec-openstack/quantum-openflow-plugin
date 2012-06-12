# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

from nova import flags
from nova import log as logging
from nova.openstack.common import cfg
from nova.virt.libvirt.vif import LibvirtOpenVswitchDriver

import quantum.plugins.nec.nova.vifinfo_client as client

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS


class LibvirtOVSVIFINFODriver(LibvirtOpenVswitchDriver):
    """
    Configure nova.conf as follows:
        libvirt_ovs_bridge=br-int
        libvirt_vif_driver=\
            quantum.plugins.nec.nova.libvirt_vif.LibvirtOVSVIFINFODriver
    """

    def plug(self, instance, network, mapping):
        conf = super(LibvirtOVSVIFINFODriver, self).plug(instance,
                                                         network,
                                                         mapping)
        interface_id = mapping['vif_uuid']
        bridge = FLAGS.libvirt_ovs_bridge
        client.update_vifinfo(interface_id, bridge,
                              conf['name'], conf['mac_address'])
        return conf

    def unplug(self, instance, network, mapping):
        interface_id = mapping['vif_uuid']
        client.delete_vifinfo(interface_id)
        super(LibvirtOVSVIFINFODriver, self).unplug(instance,
                                                    network,
                                                    mapping)

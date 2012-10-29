# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

"""
Virtual Interface Drivers for Nova to collaborate Nova, Quantum and PFC.

Configure nova.conf as follows:
    libvirt_ovs_bridge=br-int
    libvirt_vif_driver=\
        quantum.plugins.nec.nova.vif_driver_4_pfc.LibvirtOVSDriver4PFC
    linuxnet_ovs_integration_bridge=br-int
    linuxnet_interface_driver=\
        quantum.plugins.nec.nova.vif_driver_4_pfc.LinuxNetOVSDriver4PFC
"""

from nova import context
from nova import db
from nova import exception
from nova import flags
from nova import log as logging
from nova.network import linux_net
from nova.openstack.common import cfg
from nova import utils
from nova.virt.libvirt import vif

from quantum.plugins.nec.tools.client import Client


LOG = logging.getLogger('nova.' + __name__)
FLAGS = flags.FLAGS

VIFINFO_PATH = "/v1.1/extensions/nec/vifinfos/%s"
AVAILABLE_VLAN_RANGE = range(1, 4000)


class LibvirtOVSDriver4PFC(vif.LibvirtOpenVswitchDriver):

    def plug(self, instance, network, mapping):
        LOG.debug("LibvirtOVSDriver4PFC.plug(instance=%s, network=%s, "
                  "mapping=%s)" % (instance, network, mapping))
        interface_id = mapping['vif_uuid']
        net_uuid = network['id']
        net_id = get_net_id_by_uuid(net_uuid)
        vlan_id = find_availavle_vlan_id(net_id)

        result = super(LibvirtOVSDriver4PFC, self).plug(instance,
                                                        network,
                                                        mapping)
        LOG.debug("LibvirtOpenVswitchDriver.plug() returns: %s" % result)
        dev_name = result['name']
        mac = result['mac_address']
        set_net_id_to_ovs_iface(dev_name, net_id)
        set_ovs_port_tag(dev_name, vlan_id)

        bridge = FLAGS.libvirt_ovs_bridge
        update_vifinfo(interface_id, bridge, dev_name, mac, vlan_id)

        return result

    def unplug(self, instance, network, mapping):
        LOG.debug("LibvirtOVSDriver4PFC.unplug(instance=%s, network=%s, "
                  "mapping=%s)" % (instance, network, mapping))
        interface_id = mapping['vif_uuid']

        delete_vifinfo(interface_id)

        super(LibvirtOVSDriver4PFC, self).unplug(instance, network, mapping)


class LinuxNetOVSDriver4PFC(linux_net.LinuxOVSInterfaceDriver):

    def plug(self, network, mac_address, gateway=True):
        LOG.debug("LinuxNetOVSDriver4PFC.plug(network=%s, mac_address=%s, "
                  "gateway=%s)" % (network, mac_address, gateway))
        vlan_id = find_availavle_vlan_id(network['id'])

        dev_name = super(LinuxNetOVSDriver4PFC, self).plug(network,
                                                           mac_address,
                                                           gateway)
        # NOTE: No virtual_interface created for GW tap,
        #       so use 'dev_name' as 'interface_id'.
        interface_id = dev_name
        set_net_id_to_ovs_iface(dev_name, network['id'])
        set_ovs_port_tag(dev_name, vlan_id)

        bridge = FLAGS.linuxnet_ovs_integration_bridge
        update_vifinfo(interface_id, bridge, dev_name, mac_address, vlan_id)

        return dev_name

    def unplug(self, network):
        LOG.debug("LinuxNetOVSDriver4PFC.plug(network=%s)" % network)
        interface_id = self.get_dev(network)

        delete_vifinfo(interface_id)

        return super(LinuxOVSVIFINFOInterfaceDriver, self).unplug(network)


def get_net_id_by_uuid(net_uuid):
    admin_context = context.get_admin_context()
    net = db.network_get_by_uuid(admin_context, net_uuid)
    LOG.debug("get_net_id_by_uuid: net_uuid=%s, net_id=%s" % (net_uuid,
                                                              net.get('id')))
    return net['id']


def run_vsctl(*args):
    ret, left = utils.execute("ovs-vsctl", *args, run_as_root=True)
    return ret.rstrip('\n\r').strip('"')


def get_ovs_datapath_id(bridge):
    datapath_id = run_vsctl('get', 'bridge', bridge, 'datapath_id')
    return "0x" + datapath_id


def list_ports(bridge):
    return run_vsctl('list-ports', bridge).split()


def get_ovs_ofport(ovs_iface_name):
    ofport = run_vsctl('get', 'Interface', ovs_iface_name, 'ofport')
    return ofport


def get_ovs_port_tag(ovs_port_name):
    port_tag = run_vsctl('get', 'Port', ovs_port_name, 'tag')
    OVS_VLAN_TAG_NONE = '[]'
    if port_tag == OVS_VLAN_TAG_NONE:
        return ''
    else:
        return str(port_tag)


def set_ovs_port_tag(ovs_port_name, vlan_id):
    run_vsctl('set', 'Port', ovs_port_name, 'tag=%s' % vlan_id)


def get_network_id(ovs_port_name):
    net_id = run_vsctl('--', '--if-exists', 'get', 'Interface',
                       ovs_port_name, 'external_ids:net-id')
    if net_id:
        return net_id
    else:
        return ''


def set_net_id_to_ovs_iface(ovs_iface_name, net_id):
    run_vsctl('set', 'Interface', ovs_iface_name,
              "external_ids:net-id=%s" % net_id)


def find_availavle_vlan_id(network_id):
    # create vlan_map: key->str(network_id), value->str(valn_id)
    vlan_map = {}
    for port in list_ports(FLAGS.libvirt_ovs_bridge):
        port_tag = get_ovs_port_tag(port)
        net_id = get_network_id(port)
        if port_tag and net_id:
            current = vlan_map.get(net_id)
            if current and current != port_tag:
                LOG.error("VLAN MAP consistency broken. "
                          "more than one vlan_ids(%s, %s) were assigned for "
                          "network_id=%s" % (net_id, current, port_tag))
                raise exception.VirtualInterfaceCreateException()
            vlan_map.update({net_id: port_tag})
    LOG.debug("Vlan-Network map on this host: %s" % vlan_map)

    # check duplicate entry for each vlan_id.
    rmap = {}
    for n, v in vlan_map.iteritems():
        o = rmap.get(v)
        if o:
            LOG.error("VLAN MAP consistency broken. "
                      "more than one network_ids(%s, %s) were assigned to "
                      "vlan_id=%s" % (n, o, v))
            raise exception.VirtualInterfaceCreateException()
        rmap.update({v: n})

    # if the network_id already mapped to vlan_id, return it.
    v = vlan_map.get(str(network_id))
    if v:
        LOG.debug("Vlan-Network map found (network_id=%s, "
                  "vlan_id=%s)" % (network_id, v))
        return v

    # try to map same number
    v = str(network_id)
    if not rmap.get(v):
        LOG.debug("Assigned new Vlan-Network map (network_id=%s, "
                  "vlan_id=%s)" % (network_id, v))
        return v

    # find available vlan_id
    for v in AVAILABLE_VLAN_RANGE:
        if str(v) not in vlan_map.keys():
            LOG.debug("Assigned new Vlan-Network map (network_id=%s, "
                      "vlan_id=%s)" % (network_id, v))
            return str(v)

    LOG.error("find_availavle_vlan_id(): NotFound availavle vlan_id for"
              "network_id=%s" % network_id)
    raise exception.VirtualInterfaceCreateException()


def update_vifinfo(interface_id, bridge, dev_name, mac, vlan_id):
    LOG.debug("update_vifinfo(interface_id=%s, bridge=%s, dev_name=%s, "
              "mac=%s, vlan_id=%s)" % (interface_id, bridge, dev_name,
                                       mac, vlan_id))

    datapath_id = get_ovs_datapath_id(bridge)
    port_no = get_ovs_ofport(dev_name)
    client = Client(FLAGS.quantum_connection_host,
                    FLAGS.quantum_connection_port,
                    format='json')
    body = {'vifinfo': {'interface_id': interface_id,
                        'ofs_port': {'datapath_id': datapath_id,
                                     'port_no': port_no,
                                     'vlan_id': vlan_id,
                                     'mac': mac}}}
    path = VIFINFO_PATH % interface_id
    client.put(path, body=body)


def delete_vifinfo(interface_id):
    LOG.debug("update_vifinfo(interface_id=%s)" % interface_id)

    client = Client(FLAGS.quantum_connection_host,
                    FLAGS.quantum_connection_port,
                    format='json')
    path = VIFINFO_PATH % interface_id
    client.delete(path)

# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

from nova import exception
from nova import flags
from nova import log as LOG
from nova.network import linux_net
from nova import utils
from nova.virt.libvirt import netutils
from nova.virt.vif import VIFDriver

from vifinfo_client import VIFINFOClient

FLAGS = flags.FLAGS
flags.DEFINE_string('libvirt_ovs_bridge', 'br-int',
                    'Name of Integration Bridge used by Open vSwitch')
flags.DEFINE_string('quantum_host', "127.0.0.1",
                     'IP address of the quantum network service.')
flags.DEFINE_integer('quantum_port', 9696,
                     'Listening port for Quantum network service')
LOG.getLogger('nova.virt.libvirt.nec.nec_vif_driver')


class NECVIFDriver(VIFDriver):

    def get_dev_name(_self, iface_id):
        return "tap" + iface_id[0:11]

    def plug(self, instance, network, mapping):
        iface_id = mapping['vif_uuid']
        dev = self.get_dev_name(iface_id)
        if not linux_net._device_exists(dev):
            utils.execute('ip', 'tuntap', 'add', dev, 'mode', 'tap',
                          run_as_root=True)
            utils.execute('ip', 'link', 'set', dev, 'up', run_as_root=True)
        utils.execute('ovs-vsctl', '--', '--may-exist', 'add-port',
                      FLAGS.libvirt_ovs_bridge, dev,
                      '--', 'set', 'Interface', dev,
                      "external-ids:iface-id=%s" % iface_id,
                      '--', 'set', 'Interface', dev,
                      "external-ids:iface-status=active",
                      '--', 'set', 'Interface', dev,
                      "external-ids:attached-mac=%s" % mapping['mac'],
                      run_as_root=True)

        ret, left = utils.execute('ovs-vsctl', 'get', 'bridge',
                                  FLAGS.libvirt_ovs_bridge, 'datapath_id',
                                  run_as_root=True)
        datapath_id = "0x" + ret.strip('"\n')
        ret, left = utils.execute('ovs-vsctl', 'get', 'Interface',
                                  dev, 'ofport', run_as_root=True)
        port_no = ret.strip()
        client = VIFINFOClient(FLAGS.quantum_host, FLAGS.quantum_port)
        client.create_vifinfo(mapping['vif_uuid'], datapath_id, port_no)

        result = {'script': '', 'name': dev, 'mac_address': mapping['mac']}
        return result

    def unplug(self, instance, network, mapping):
        dev = self.get_dev_name(mapping['vif_uuid'])
        client = VIFINFOClient(FLAGS.quantum_host, FLAGS.quantum_port)
        client.delete_vifinfo(mapping['vif_uuid'])
        try:
            utils.execute('ovs-vsctl', 'del-port',
                          FLAGS.libvirt_ovs_bridge, dev, run_as_root=True)
            utils.execute('ip', 'link', 'delete', dev, run_as_root=True)
        except exception.ProcessExecutionError:
            LOG.warning(_("Failed while unplugging vif of instance '%s'"),
                        instance['name'])
            raise

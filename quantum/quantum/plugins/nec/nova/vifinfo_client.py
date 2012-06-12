# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

from nova import flags
from nova import log as logging
from nova.openstack.common import cfg
from nova import utils

from quantum.plugins.nec.tools.client import Client

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS

vifinfos_path = "/v1.1/extensions/nec/vifinfos"
vifinfo_path = "/v1.1/extensions/nec/vifinfos/%s"


def create_vifinfo(interface_id, bridge, dev, mac_address):
    ret, left = utils.execute('ovs-vsctl', 'get', 'bridge', bridge,
                            'datapath_id', run_as_root=True)
    datapath_id = "0x" + ret.strip('"\n')
    ret, left = utils.execute('ovs-vsctl', 'get', 'Interface', dev, 'ofport',
                                run_as_root=True)
    port_no = ret.strip()
    client = Client(FLAGS.quantum_connection_host,
                    FLAGS.quantum_connection_port,
                    format='json')
    body = {'vifinfo': {'interface_id': interface_id,
                        'ofs_port': {'datapath_id': datapath_id,
                                     'port_no': port_no,
                                     'mac': mac_address}}}
    client.post(vifinfos_path, body=body)


def update_vifinfo(interface_id, bridge, dev, mac_address):
    ret, left = utils.execute('ovs-vsctl', 'get', 'bridge', bridge,
                            'datapath_id', run_as_root=True)
    datapath_id = "0x" + ret.strip('"\n')
    ret, left = utils.execute('ovs-vsctl', 'get', 'Interface', dev, 'ofport',
                                run_as_root=True)
    port_no = ret.strip()
    client = Client(FLAGS.quantum_connection_host,
                    FLAGS.quantum_connection_port,
                    format='json')
    body = {'vifinfo': {'interface_id': interface_id,
                        'ofs_port': {'datapath_id': datapath_id,
                                     'port_no': port_no,
                                     'mac': mac_address}}}
    path = vifinfo_path % interface_id
    client.put(path, body=body)


def delete_vifinfo(interface_id):
    client = Client(FLAGS.quantum_connection_host,
                    FLAGS.quantum_connection_port,
                    format='json')
    path = vifinfo_path % interface_id
    client.delete(path)

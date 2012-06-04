# vim: tabstop=4 shiftwidth=4 softtabstop=4

import logging
import unittest

from quantum.db import api as db

import quantum.plugins.nec.db.nec_db as ndb
import quantum.plugins.nec.db.nec_models as nmodels
import quantum.plugins.nec.db.quantum_db_extension as dbe

LOG = logging.getLogger(__name__)


class QuantumDBExtensionTest(unittest.TestCase):

    def setUp(self):
        db.configure_db({'sql_connection': 'sqlite:///:memory:'})
        LOG.debug("Setup")
        self._create_target()

    def _create_target(self):
        tenant_id = "tenant1"
        net_name = "network1"
        self.vif_id = "vif1"
        net = db.network_create(tenant_id, net_name)
        self.port = db.port_create(net.uuid)
        db.port_set_attachment(self.port.uuid, net.uuid, self.vif_id)

    def tearDown(self):
        db.clear_db()

    def test_get_plugged_port(self):
        ret = dbe.get_plugged_port(self.vif_id)
        self.assertTrue(ret.uuid == self.port.uuid)
        ret = dbe.get_plugged_port("vif-none")
        self.assertTrue(ret == None)


class NECDBTest(unittest.TestCase):

    def setUp(self):
        db.configure_db({'sql_connection': 'sqlite:///:memory:'})
        LOG.debug("Setup")

    def tearDown(self):
        db.clear_db()

    def test_initialize(self):
        class config(object):
            def __init__(self):
                self.DB = 'sqlite:///:memory:'

        ndb.initialize(config())

    def test_get_ofn_tenant(self):
        tenant_id = "tenant_get"
        ofn_tenant_id = "ofn_tenant_get"
        ret = ndb.get_ofn_tenant(tenant_id)
        self.assertTrue(ret == None)
        ret = ndb.add_ofn_tenant(ofn_tenant_id, tenant_id)
        ret = ndb.get_ofn_tenant(tenant_id)
        self.assertTrue(ret.tenant_id == tenant_id)
        self.assertTrue(ret.ofn_tenant_id == ofn_tenant_id)
        ndb.del_ofn_tenant(tenant_id)

    def test_add_ofn_tenant(self):
        tenant_id = "tenant_add"
        ofn_tenant_id = "ofn_tenant_add"
        ret = ndb.add_ofn_tenant(ofn_tenant_id, tenant_id)
        self.assertTrue(ret.tenant_id == tenant_id)
        self.assertTrue(ret.ofn_tenant_id == ofn_tenant_id)
        ret = ndb.get_ofn_tenant(tenant_id)
        self.assertTrue(ret.tenant_id == tenant_id)
        self.assertTrue(ret.ofn_tenant_id == ofn_tenant_id)
        ndb.del_ofn_tenant(tenant_id)

    def test_del_ofn_tenant(self):
        tenant_id = "tenant_del"
        ofn_tenant_id = "ofn_tenant_del"
        ret = ndb.add_ofn_tenant(ofn_tenant_id, tenant_id)
        ret = ndb.get_ofn_tenant(tenant_id)
        self.assertTrue(ret.tenant_id == tenant_id)
        self.assertTrue(ret.ofn_tenant_id == ofn_tenant_id)
        ndb.del_ofn_tenant(tenant_id)
        ret = ndb.get_ofn_tenant(tenant_id)
        self.assertTrue(ret == None)

    def test_get_ofn_network(self):
        network_id = "network_get"
        ofn_network_id = "ofn_network_get"
        ret = ndb.get_ofn_network(network_id)
        self.assertTrue(ret == None)
        ret = ndb.add_ofn_network(ofn_network_id, network_id)
        ret = ndb.get_ofn_network(network_id)
        self.assertTrue(ret.network_id == network_id)
        self.assertTrue(ret.ofn_network_id == ofn_network_id)
        ndb.del_ofn_network(network_id)

    def test_add_ofn_network(self):
        network_id = "network_add"
        ofn_network_id = "ofn_network_add"
        ret = ndb.add_ofn_network(ofn_network_id, network_id)
        self.assertTrue(ret.network_id == network_id)
        self.assertTrue(ret.ofn_network_id == ofn_network_id)
        ret = ndb.get_ofn_network(network_id)
        self.assertTrue(ret.network_id == network_id)
        self.assertTrue(ret.ofn_network_id == ofn_network_id)
        ndb.del_ofn_network(network_id)

    def test_del_ofn_network(self):
        network_id = "network_del"
        ofn_network_id = "ofn_network_del"
        ret = ndb.add_ofn_network(ofn_network_id, network_id)
        ret = ndb.get_ofn_network(network_id)
        self.assertTrue(ret.network_id == network_id)
        self.assertTrue(ret.ofn_network_id == ofn_network_id)
        ndb.del_ofn_network(network_id)
        ret = ndb.get_ofn_network(network_id)
        self.assertTrue(ret == None)

    def test_get_ofn_port(self):
        port_id = "port_get"
        ofn_port_id = "ofn_port_get"
        ret = ndb.get_ofn_port(port_id)
        self.assertTrue(ret == None)
        ret = ndb.add_ofn_port(ofn_port_id, port_id)
        ret = ndb.get_ofn_port(port_id)
        self.assertTrue(ret.port_id == port_id)
        self.assertTrue(ret.ofn_port_id == ofn_port_id)
        ndb.del_ofn_port(port_id)

    def test_add_ofn_port(self):
        port_id = "port_add"
        ofn_port_id = "ofn_port_add"
        ret = ndb.add_ofn_port(ofn_port_id, port_id)
        self.assertTrue(ret.port_id == port_id)
        self.assertTrue(ret.ofn_port_id == ofn_port_id)
        ret = ndb.get_ofn_port(port_id)
        self.assertTrue(ret.port_id == port_id)
        self.assertTrue(ret.ofn_port_id == ofn_port_id)
        ndb.del_ofn_port(port_id)

    def test_del_ofn_port(self):
        port_id = "port_del"
        ofn_port_id = "ofn_port_del"
        ret = ndb.add_ofn_port(ofn_port_id, port_id)
        ret = ndb.get_ofn_port(port_id)
        self.assertTrue(ret.port_id == port_id)
        self.assertTrue(ret.ofn_port_id == ofn_port_id)
        ndb.del_ofn_port(port_id)
        ret = ndb.get_ofn_port(port_id)
        self.assertTrue(ret == None)

    def test_get_vifinfo(self):
        interface_id = "interface_get"
        datapath_id = "datapath_get"
        port_no = 1
        vlan_id = 101
        ret = ndb.get_vifinfo(interface_id)
        self.assertTrue(ret == None)
        ndb.add_vifinfo(interface_id, datapath_id, port_no, vlan_id)
        ret = ndb.get_vifinfo(interface_id)
        self.assertTrue(ret.interface_id == interface_id)
        self.assertTrue(ret.datapath_id == datapath_id)
        self.assertTrue(ret.port_no == port_no)
        self.assertTrue(ret.vlan_id == vlan_id)
        ndb.del_vifinfo(interface_id)

    def test_list_vifinfos(self):
        interface_ida = "interface_lista"
        datapath_ida = "datapath_lista"
        port_noa = 2
        vlan_ida = 102
        interface_idb = "interface_listb"
        datapath_idb = "datapath_listb"
        port_nob = 3
        vlan_idb = 103
        ret = ndb.list_vifinfos()
        self.assertTrue(len(ret) == 0)
        ndb.add_vifinfo(interface_ida, datapath_ida, port_noa, vlan_ida)
        ret = ndb.list_vifinfos()
        self.assertTrue(len(ret) == 1)
        ndb.add_vifinfo(interface_idb, datapath_idb, port_nob, vlan_idb)
        ret = ndb.list_vifinfos()
        self.assertTrue(len(ret) == 2)
        for vifinfo in ret:
            if vifinfo.interface_id == interface_ida:
                self.assertTrue(vifinfo.datapath_id == datapath_ida)
                self.assertTrue(vifinfo.port_no == port_noa)
                self.assertTrue(vifinfo.vlan_id == vlan_ida)
            elif vifinfo.interface_id == interface_idb:
                self.assertTrue(vifinfo.datapath_id == datapath_idb)
                self.assertTrue(vifinfo.port_no == port_nob)
                self.assertTrue(vifinfo.vlan_id == vlan_idb)
            else:
                self.fail("returned list includes unknown interface_id.")
        ndb.del_vifinfo(interface_ida)
        ndb.del_vifinfo(interface_idb)

    def test_add_vifinfo(self):
        interface_id = "interface_add"
        datapath_id = "datapath_add"
        port_no = 4
        vlan_id = 104
        ret = ndb.add_vifinfo(interface_id, datapath_id, port_no)
        self.assertTrue(ret.interface_id == interface_id)
        self.assertTrue(ret.datapath_id == datapath_id)
        self.assertTrue(ret.port_no == port_no)
        self.assertTrue(ret.vlan_id == 65535)
        ret = ndb.get_vifinfo(interface_id)
        self.assertTrue(ret.interface_id == interface_id)
        self.assertTrue(ret.datapath_id == datapath_id)
        self.assertTrue(ret.port_no == port_no)
        self.assertTrue(ret.vlan_id == 65535)
        ndb.del_vifinfo(interface_id)
        ret = ndb.add_vifinfo(interface_id, datapath_id, port_no, vlan_id)
        self.assertTrue(ret.interface_id == interface_id)
        self.assertTrue(ret.datapath_id == datapath_id)
        self.assertTrue(ret.port_no == port_no)
        self.assertTrue(ret.vlan_id == vlan_id)
        ret = ndb.get_vifinfo(interface_id)
        self.assertTrue(ret.interface_id == interface_id)
        self.assertTrue(ret.datapath_id == datapath_id)
        self.assertTrue(ret.port_no == port_no)
        self.assertTrue(ret.vlan_id == vlan_id)
        ndb.del_vifinfo(interface_id)

    def test_del_vifinfo(self):
        interface_id = "interface_del"
        datapath_id = "datapath_del"
        port_no = 5
        vlan_id = 105
        ndb.add_vifinfo(interface_id, datapath_id, port_no)
        ndb.del_vifinfo(interface_id)
        ret = ndb.get_vifinfo(interface_id)
        self.assertTrue(ret == None)

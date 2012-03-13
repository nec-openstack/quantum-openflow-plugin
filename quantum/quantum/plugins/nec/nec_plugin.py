# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import ConfigParser
import logging
from webob import exc as h_exc

from quantum.common import exceptions as exc
from quantum.db import api as db
from quantum.quantum_plugin_base import QuantumPluginBase

from quantum.plugins.nec.db import nec_db as ndb
from quantum.plugins.nec.db import quantum_db_extension as dbe
from quantum.plugins.nec.nec_plugin_config import NECConfig
from quantum.plugins.nec.ofnet.ofnetwork import OFNetwork

LOG = logging.getLogger('nec_plugin')


class NECPlugin(QuantumPluginBase):
    """The Quantum NEC Plug-in controls an OpenFlow Controller.

    The Quantum NEC Plug-in maps L2 logical networks to L2 virtualized networks
    on an OpenFlow enabled network.  An OpenFlow Controller (OFC) provides
    L2 network isolation without VLAN and this plugin controls the OFC.

    :param tenant_id:       Logical Tenant ID on Quantum
    :param network_id:      Logical Network ID on Quantum
    :param port_id:         Logical Port ID on Quantum
    :param ofn_tenant_id:   Virtual Tenant ID on OFC
    :param ofn_network_id:  Virtual Network ID on OFC
    :param ofn_port_id:     Virtual Port ID on OFC
    :param vifinfo:         Virtual Interface Information in the domain of OFC

    The IDs like ofn_* could be generated by NEC Plug-in or OFC.
    It depends on an implementation of OFC,
    and users must configure NEC Plug-in which generate these IDs.
    """

    def __init__(self, config_file=None):
        self.conf = NECConfig(config_file)
        self.ofn = OFNetwork(self.conf.OFC_HOST, self.conf.OFC_PORT)
        ndb.initialize(self.conf)
        if self.conf.vif_file:
            vifinfo_list = self.conf.load_vifinfo(self.conf.vif_file)
            for vifinfo in vifinfo_list:
                old_vifinfo = ndb.get_vifinfo(vifinfo['interface_id'])
                if old_vifinfo:
                    LOG.info("Delete old vifinfo %s." % old_vifinfo)
                    ndb.del_vifinfo(vifinfo['interface_id'])
                ndb.add_vifinfo(vifinfo['interface_id'],
                                vifinfo['datapath_id'],
                                vifinfo['port_no'],
                                vifinfo['vlan_id'])

    def _create_ofn_tenant(self, tenant_id):
        ofn_tenant = ndb.get_ofn_tenant(tenant_id)
        if ofn_tenant:
            ofn_tenant_id = ofn_tenant.ofn_tenant_id
        else:
            if self.conf.auto_id_tenant:
                """get ofn_tenant_id from OFN."""
                res = self.ofn.ofn_create_tenant(tenant_id)
                ofn_tenant_id = res['id']
                LOG.debug("_create_ofn_tenant(): "
                          "ofn_create_tenant() return '%s'" % res)
            else:
                ofn_tenant_id = tenant_id
                """
                Don't POST it to OFC, because Sliceable DO NOT handle tenant.
                """
            LOG.debug("_create_ofn_tenant(): create new ofn_tenant %s"
                      "for tenant %s." % (tenant_id, ofn_tenant_id))
            ndb.add_ofn_tenant(ofn_tenant_id, tenant_id)
        return ofn_tenant_id

    def _delete_orphan_ofn_tenant(self, tenant_id):
        num_of_networks = len(db.network_list(tenant_id))
        if num_of_networks == 0:
            ofn_tenant = ndb.get_ofn_tenant(tenant_id)
            if ofn_tenant and self.conf.auto_id_tenant:
                self.ofn.ofn_delete_tenant(ofn_tenant.ofn_tenant_id)
                ndb.del_ofn_tenant(tenant_id)

    def _get_ofn_tenant_id(self, tenant_id):
        ofn_tenant = ndb.get_ofn_tenant(tenant_id)
        if not ofn_tenant:
            LOG.warning("_get_ofn_tenant_id(): ofn_tenant not found "
                        "(tenant_id = %s)" % tenant_id)
            raise h_exc.HTTPInternalServerError(\
              "NotFound ofn_tenant_id for tenant_id %s." % tenant_id)
        return ofn_tenant.ofn_tenant_id

    def _get_ofn_network_id(self, network_id):
        ofn_network = ndb.get_ofn_network(network_id)
        if not ofn_network:
            LOG.warning("_get_ofn_network_id(): ofn_network not found "
                        "(network_id = %s)" % network_id)
            raise h_exc.HTTPInternalServerError(\
              "NotFound ofn_network_id for network_id %s." % network_id)
        return ofn_network.ofn_network_id

    def _get_ofn_port_id(self, port_id):
        ofn_port = ndb.get_ofn_port(port_id)
        if not ofn_port:
            LOG.warning("_get_ofn_port_id(): ofn_port not found "
                        "(port_id = %s)" % port_id)
            raise h_exc.HTTPInternalServerError(\
              "NotFound ofn_port_id for port_id %s." % port_id)
        return ofn_port.ofn_port_id

    def _get_ofn_filter_id(self, filter_id):
        ofn_filter = ndb.get_ofn_filter(filter_id)
        if not ofn_filter:
            LOG.warning("_get_ofn_filter_id(): ofn_filter not found "
                        "(filter_id = %s)" % filter_id)
            raise h_exc.HTTPInternalServerError(\
              "NotFound ofn_filter_id for filter_id %s." % filter_id)
        return ofn_filter.ofn_filter_id

    def _get_network(self, tenant_id, network_id):
        network = db.network_get(network_id)
        # Network must exist and belong to the appropriate tenant.
        if network.tenant_id != tenant_id:
            LOG.warning("_get_network(): mismatch tenant_id = %s, "
                        "network_id = %s, network.tenant_id = %s" %
                        (tenant_id, network_id, network.tenant_id))
            raise exc.NetworkNotFound(net_id=network_id)
        return network

    def _get_port(self, tenant_id, network_id, port_id):
        network = self._get_network(tenant_id, network_id)
        port = db.port_get(port_id, network_id)
        # Port must exist and belong to the appropriate network.
        if port.network_id != network_id:
            LOG.warning("_get_port(): mismatch network_id = %s, "
                        "port_id = %s, port.network_id = %s" %
                        (network_id, port_id, port.network_id))
            raise exc.PortNotFound(net_id=network_id, port_id=port_id)
        return port

    def _get_filter(self, tenant_id, network_id, filter_id):
        network = self._get_network(tenant_id, network_id)
        filter = ndb.get_filter(filter_id, network_id)
        if not filter:
            raise h_exc.HTTPNotFound("Filter %s could not be found "
                                    "on network %s" % (filter_id, network_id))
        # Filter must exist and belong to the appropriate network.
        if filter.network_id != network_id:
            LOG.warning("_get_filter(): mismatch network_id = %s, "
                        "filter_id = %s, port.network_id = %s" %
                        (network_id, filter_id, filter.network_id))
            raise h_exc.HTTPNotFound("Filter %s could not be found "
                                    "on network %s" % (filter_id, network_id))
        return filter

    def _validate_port_state(self, port_state):
        if port_state.upper() not in ("ACTIVE", "DOWN"):
            raise exc.StateInvalid(port_state=port_state)
        return True

    def _port_attachable(self, port):
        if not port:
            LOG.debug("_port_attachable(): no port.")
            return False
        if not port.interface_id:
            LOG.debug("_port_attachable(): no port.interface_id.")
            return False
        if not port.state.upper() in "ACTIVE":
            LOG.debug("_port_attachable(): port.state is not ACTIVE.")
            return False
        if not ndb.get_vifinfo(port.interface_id):
            LOG.debug("_port_attachable(): no vifinfo for the port.")
            return False
        return True

    def _attach(self, tenant_id, network_id, port_id, interface_id):
        LOG.debug("_attach(): called")
        ofn_tenant_id = self._get_ofn_tenant_id(tenant_id)
        ofn_network_id = self._get_ofn_network_id(network_id)
        vifinfo = ndb.get_vifinfo(interface_id)

        if self.conf.auto_id_port:
            """id include response."""
            res = self.ofn.ofn_create_port(ofn_tenant_id,
                                           ofn_network_id,
                                           vifinfo.datapath_id,
                                           str(vifinfo.port_no),
                                           str(vifinfo.vlan_id))
            ofn_port_id = res['id']
        else:
            """use uuid for ofn_network."""
            ofn_port_id = port_id
            res = self.ofn.ofn_create_port(ofn_tenant_id,
                                           ofn_network_id,
                                           vifinfo.datapath_id,
                                           str(vifinfo.port_no),
                                           str(vifinfo.vlan_id),
                                           ofn_port_id)
        LOG.debug("_attach(): ofn_create_port() return '%s'" % res)
        LOG.debug("_attach(): ofn_port_id = %s" % ofn_port_id)
        ndb.add_ofn_port(ofn_port_id, port_id)

        port = self._get_port(tenant_id, network_id, port_id)
        for filter in ndb.get_associated_filters(network_id, port_id):
            self._enable_filter(tenant_id, filter, network_id, port)

    def _detach(self, tenant_id, network_id, port_id):
        LOG.debug("_detach(): called")
        ofn_tenant_id = self._get_ofn_tenant_id(tenant_id)
        ofn_network_id = self._get_ofn_network_id(network_id)
        ofn_port_id = self._get_ofn_port_id(port_id)
        res = self.ofn.ofn_delete_port(ofn_tenant_id,
                                       ofn_network_id,
                                       ofn_port_id)
        LOG.debug("_detach(): ofn_delete_port() return '%s'" % res)
        ndb.del_ofn_port(port_id)

        port = self._get_port(tenant_id, network_id, port_id)
        for filter in ndb.get_associated_filters(network_id, port_id):
            self._disable_filter(tenant_id, filter.uuid)

    def get_all_networks(self, tenant_id):
        """
        Returns a dictionary containing all
        <network_uuid, network_name> for
        the specified tenant.
        """
        LOG.debug("get_all_networks() called")
        networks = []
        for network in db.network_list(tenant_id):
            network_item = {'net-id': network.uuid, 'net-name': network.name}
            networks.append(network_item)
        return networks

    def get_network_details(self, tenant_id, network_id):
        """
        retrieved a list of all the remote vifs that
        are attached to the network
        """
        LOG.debug("get_network_details() called")
        network = self._get_network(tenant_id, network_id)
        # Retrieves ports for network
        ports = self.get_all_ports(tenant_id, network_id)
        return {'net-id': network.uuid,
                'net-name': network.name,
                'net-ports': ports}

    def create_network(self, tenant_id, network_name):
        """
        Creates a new Virtual Network, and assigns it
        a symbolic name.
        """
        LOG.debug("create_network() called")
        ofn_tenant_id = self._create_ofn_tenant(tenant_id)
        new_network = db.network_create(tenant_id, network_name)

        try:
            if self.conf.auto_id_network:
                """Auto ID is ture. id include response."""
                res = self.ofn.ofn_create_network(ofn_tenant_id, network_name)
                ofn_network_id = res['id']
            else:
                """Auto ID is false. use uuid for ofn_network."""
                ofn_network_id = new_network.uuid
                res = self.ofn.ofn_create_network(ofn_tenant_id,
                                                  network_name,
                                                  ofn_network_id)
        except Exception:
            db.network_destroy(new_network.uuid)
            LOG.error("create_network() failed on OFC.")
            raise h_exc.HTTPInternalServerError(\
              "Failed to create network on OFC.")

        LOG.debug("create_network(): ofn_create_network() return '%s'" % res)
        LOG.debug("create_network(): ofn_network_id = %s" % ofn_network_id)
        ndb.add_ofn_network(ofn_network_id, new_network.uuid)
        return {'net-id': new_network.uuid, 'net-name': new_network.name}

    def delete_network(self, tenant_id, network_id):
        """
        Deletes the network with the specified network identifier
        belonging to the specified tenant.
        """
        LOG.debug("delete_network() called")
        network = self._get_network(tenant_id, network_id)
        # Verify that the network has no port
        for port in db.port_list(network_id):
            if port:
                raise exc.NetworkInUse(network_id=network_id)

        ofn_tenant_id = self._get_ofn_tenant_id(tenant_id)
        ofn_network_id = self._get_ofn_network_id(network_id)
        self.ofn.ofn_delete_network(ofn_tenant_id, ofn_network_id)
        ndb.del_ofn_network(network_id)

        db.network_destroy(network_id)
        self._delete_orphan_ofn_tenant(tenant_id)
        return {'net-id': network.uuid}

    def rename_network(self, tenant_id, network_id, new_name):
        """
        Updates the symbolic name belonging to a particular
        Virtual Network.
        """
        LOG.debug("rename_network() called")
        # verify network_id
        self._get_network(tenant_id, network_id)
        network = db.network_rename(network_id, tenant_id, new_name)
        ofn_tenant_id = self._get_ofn_tenant_id(tenant_id)
        ofn_network_id = self._get_ofn_network_id(network_id)
        res = self.ofn.ofn_rename_network(ofn_tenant_id,
                                          ofn_network_id,
                                          new_name)
        LOG.debug("rename_network(): ofn_rename_network() return '%s'" % res)
        return {'net-id': network.uuid, 'net-name': network.name}

    def get_all_ports(self, tenant_id, network_id):
        """
        Retrieves all port identifiers belonging to the
        specified Virtual Network.
        """
        LOG.debug("get_all_ports() called")
        # verify network_id
        self._get_network(tenant_id, network_id)
        ports = db.port_list(network_id)
        port_ids = []
        for x in ports:
            port_id = {'port-id': x.uuid}
            port_ids.append(port_id)
        return port_ids

    def get_port_details(self, tenant_id, network_id, port_id):
        """
        This method allows the user to retrieve a remote interface
        that is attached to this particular port.
        """
        LOG.debug("get_port_details() called")
        port = self._get_port(tenant_id, network_id, port_id)
        return {'port-id': port.uuid,
                'net-id': port.network_id,
                'attachment': port.interface_id,
                'port-state': port.state}

    def create_port(self, tenant_id, network_id, port_state=None):
        """
        Creates a port on the specified Virtual Network.
        """
        LOG.debug("create_port() called")
        # verify network_id
        self._get_network(tenant_id, network_id)
        port_state_up = None
        if port_state:
            self._validate_port_state(port_state)
            port_state_up = port_state.upper()
        port = db.port_create(network_id, port_state_up)
        LOG.debug("create_port(): port state is %s" % port.state)
        return {'port-id': port.uuid}

    def update_port(self, tenant_id, network_id, port_id, new_state):
        """
        Updates the state of a port on the specified Virtual Network.
        """
        LOG.debug("update_port() called")
        port = self._get_port(tenant_id, network_id, port_id)
        self._validate_port_state(new_state)
        new_state_up = new_state.upper()
        old_state_up = port.state.upper()
        if old_state_up == new_state_up:
            LOG.debug("update_port(): port state was not changed.")
            return {'port-id': port.uuid, 'port-state': port.state}
        if new_state_up in "DOWN":
            if self._port_attachable(port):
                self._detach(tenant_id, network_id, port_id)
        port = db.port_set_state(port_id, network_id, new_state_up)
        if new_state_up in "ACTIVE":
            if self._port_attachable(port):
                self._attach(tenant_id, network_id, port_id, port.interface_id)
        return {'port-id': port.uuid, 'port-state': port.state}

    def delete_port(self, tenant_id, network_id, port_id):
        """
        Deletes a port on a specified Virtual Network,
        if the port contains a remote interface attachment,
        the remote interface is first un-plugged and then the port
        is deleted.
        """
        LOG.debug("delete_port() called")
        port = self._get_port(tenant_id, network_id, port_id)
        if port.interface_id:
            raise exc.PortInUse(net_id=network_id,
                                port_id=port_id,
                                att_id=port.interface_id)
        db.port_destroy(port_id, network_id)
        return {'port-id': port.uuid}

    def plug_interface(self, tenant_id, network_id, port_id, interface_id):
        """
        Attaches a remote interface to the specified port on the
        specified Virtual Network.
        """
        LOG.debug("plug_interface() called")
        port = self._get_port(tenant_id, network_id, port_id)

        # Validate attachment
        if port.interface_id:
            raise exc.PortInUse(net_id=network_id,
                                port_id=port_id,
                                att_id=port.interface_id)
        p = dbe.get_plugged_port(interface_id)
        if p:
            raise exc.AlreadyAttached(net_id=network_id,
                                      port_id=port_id,
                                      att_id=interface_id,
                                      att_port_id=p.uuid)

        port = db.port_set_attachment(port_id, network_id, interface_id)
        if self._port_attachable(port):
            self._attach(tenant_id, network_id, port_id, interface_id)

    def unplug_interface(self, tenant_id, network_id, port_id):
        """
        Detaches a remote interface from the specified port on the
        specified Virtual Network.
        """
        LOG.debug("unplug_interface() called")
        port = self._get_port(tenant_id, network_id, port_id)
        if self._port_attachable(port):
            self._detach(tenant_id, network_id, port_id)
        db.port_unset_attachment(port_id, network_id)

    supported_extension_aliases = ["VIFINFOS", "FILTERS"]

    def get_vifinfo(self, interface_id):
        LOG.debug("get_vifinfo() called")
        vifinfo = ndb.get_vifinfo(interface_id)
        if not vifinfo:
            return None
        return {'vifinfo': {
                  'interface_id': vifinfo.interface_id,
                  'ofs_port': {'datapath_id': vifinfo.datapath_id,
                               'port_no': str(vifinfo.port_no),
                               'vlan_id': str(vifinfo.vlan_id)}}}

    def list_vifinfos(self):
        LOG.debug("list_vifinfos() called")
        vifs = ndb.list_vifinfos()
        id_list = [{'interface_id': vif.interface_id} for vif in vifs]
        return {'vifinfos': id_list}

    def add_vifinfo(self, interface_id, datapath_id, port_no, vlan_id=65535):
        LOG.debug("add_vifinfo() called")
        ndb.add_vifinfo(interface_id, datapath_id, port_no, vlan_id)
        port = dbe.get_plugged_port(interface_id)
        if self._port_attachable(port):
            network = db.network_get(port.network_id)
            self._attach(network.tenant_id, network.uuid, port.uuid,
                         interface_id)

    def delete_vifinfo(self, interface_id):
        LOG.debug("delete_vifinfo() called")
        port = dbe.get_plugged_port(interface_id)
        if self._port_attachable(port):
            network = db.network_get(port.network_id)
            self._detach(network.tenant_id, network.uuid, port.uuid)
        ndb.del_vifinfo(interface_id)

    def _enable_filter(self, tenant_id, filter, network_id, port=None):
        LOG.debug("_enable_filter() called.")
        ofn_tenant_id = self._get_ofn_tenant_id(tenant_id)
        ofn_network_id = self._get_ofn_network_id(network_id)
        if port:
            vifinfo = ndb.get_vifinfo(port.interface_id)
            if not vifinfo:
                LOG.error("_enable_filter(): failed to get vifinfo of "
                          "port.uuid %s port.interface_id %s" %
                          (port.uuid, port.interface_id))
                raise h_exc.HTTPInternalServerError(\
                  "NotFound vifinfo of port %s." % port.uuid)
        else:
            vifinfo = None

        if self.conf.auto_id_filter:
            """id include response."""
            res = self.ofn.ofn_create_filter(ofn_tenant_id, ofn_network_id,
                                             filter, vifinfo)
            ofn_filter_id = res['id']
        else:
            """use uuid for ofn_filter."""
            ofn_filter_id = filter.uuid
            res = self.ofn.ofn_create_filter(ofn_tenant_id, ofn_network_id,
                                             filter, vifinfo, ofn_filter_id)
        LOG.debug("_enable_filter(): ofn_create_filter() return '%s'", res)
        LOG.debug("_enable_filter(): ofn_filter_id = %s", ofn_filter_id)
        ndb.add_ofn_filter(ofn_filter_id, filter.uuid)

    def _disable_filter(self, tenant_id, filter_id):
        LOG.debug("_disable_filter() called.")
        ofn_tenant_id = self._get_ofn_tenant_id(tenant_id)
        ofn_filter_id = self._get_ofn_filter_id(filter_id)
        res = self.ofn.ofn_delete_filter(ofn_tenant_id, ofn_filter_id)
        LOG.debug("_disable_filter(): ofn_delete_filter() return '%s'" % res)
        ndb.del_ofn_filter(filter_id)

    def _validate_port_in_filter_dict(self, tenant_id, network_id, filter_dict):
        condition = filter_dict.get('condition', None)
        if condition:
            port_id = filter_dict['condition'].get('in_port', None)
            if port_id:
                port = self._get_port(tenant_id, network_id, port_id)

    def get_filter(self, tenant_id, network_id, filter_id):
        LOG.debug("get_filter() called.")
        filter = self._get_filter(tenant_id, network_id, filter_id)
        return filter.dic()

    def list_filters(self, tenant_id, network_id):
        LOG.debug("list_filters() called.")
        self._get_network(tenant_id, network_id)
        filters = ndb.list_filters(network_id)
        id_list = [{'id': filter.uuid} for filter in filters]
        return {'filters': id_list}

    def add_filter(self, tenant_id, network_id, filter_dict):
        LOG.debug("add_filter() called")
        self._get_network(tenant_id, network_id)
        self._validate_port_in_filter_dict(tenant_id, network_id, filter_dict)
        filter = ndb.add_filter(network_id, filter_dict)
        if filter.in_port:
            port = self._get_port(tenant_id, network_id, filter.in_port)
            if self._port_attachable(port):
                self._enable_filter(tenant_id, filter, network_id, port)
        else:
            self._enable_filter(tenant_id, filter, network_id)
        return {'filter': {'id': filter.uuid}}

    def update_filter(self, tenant_id, network_id, filter_id, filter_dict):
        LOG.debug("update_filter() called")
        self._validate_port_in_filter_dict(tenant_id, network_id, filter_dict)
        filter = self._get_filter(tenant_id, network_id, filter_id)
        if filter.in_port:
            port = self._get_port(tenant_id, network_id, filter.in_port)
            if self._port_attachable(port):
                self._disable_filter(tenant_id, filter_id)
        else:
            self._disable_filter(tenant_id, filter_id)
        filter = ndb.update_filter(filter_id, network_id, filter_dict)
        if filter.in_port:
            port = self._get_port(tenant_id, network_id, filter.in_port)
            if self._port_attachable(port):
                self._enable_filter(tenant_id, filter, network_id, port)
        else:
            self._enable_filter(tenant_id, filter, network_id)

    def delete_filter(self, tenant_id, network_id, filter_id):
        LOG.debug("delete_filter() called")
        filter = self._get_filter(tenant_id, network_id, filter_id)
        if filter.in_port:
            port = self._get_port(tenant_id, network_id, filter.in_port)
            if self._port_attachable(port):
                self._disable_filter(tenant_id, filter_id)
        else:
            self._disable_filter(tenant_id, filter_id)
        ndb.del_filter(filter_id, network_id)

# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import logging
from sqlalchemy.orm import exc

from quantum.common import exceptions as q_exc
import quantum.db.api as db

import nec_models

LOG = logging.getLogger('nec_plugin.nec_db')


def initialize(conf):
    options = {'sql_connection': conf.DB}
    LOG.debug("Configure DB: %s" % options)
    db.configure_db(options)


def get_ofn_tenant(tenant_id):
    session = db.get_session()
    try:
        return session.query(nec_models.OFNTenant).\
          filter_by(tenant_id=tenant_id).\
          one()
    except exc.NoResultFound:
        return None


def add_ofn_tenant(ofn_tenant_id, tenant_id):
    session = db.get_session()
    ofntenant = nec_models.OFNTenant(ofn_tenant_id, tenant_id)
    session.add(ofntenant)
    session.flush()
    return ofntenant


def del_ofn_tenant(tenant_id):
    session = db.get_session()
    try:
        ofntenant = session.query(nec_models.OFNTenant).\
          filter_by(tenant_id=tenant_id).\
          one()
        session.delete(ofntenant)
        session.flush()
    except exc.NoResultFound:
        LOG.warning("del_ofn_tenant(): NotFound ofn_tenant for "
                    "tenant_id: %s" % tenant_id)


def get_ofn_network(network_id):
    session = db.get_session()
    try:
        return session.query(nec_models.OFNNetwork).\
          filter_by(network_id=network_id).\
          one()
    except exc.NoResultFound:
        return None


def add_ofn_network(ofn_network_id, network_id):
    session = db.get_session()
    ofn_network = nec_models.OFNNetwork(ofn_network_id, network_id)
    session.add(ofn_network)
    session.flush()
    return ofn_network


def del_ofn_network(network_id):
    session = db.get_session()
    try:
        ofn_network = session.query(nec_models.OFNNetwork).\
          filter_by(network_id=network_id).\
          one()
        session.delete(ofn_network)
        session.flush()
    except exc.NoResultFound:
        LOG.warning("del_ofn_network(): NotFound ofn_network for "
                    "network_id %s" % network_id)


def get_ofn_port(port_id):
    session = db.get_session()
    try:
        return session.query(nec_models.OFNPort).\
          filter_by(port_id=port_id).\
          one()
    except exc.NoResultFound:
        return None


def add_ofn_port(ofn_port_id, port_id):
    session = db.get_session()
    ofn_port = nec_models.OFNPort(ofn_port_id, port_id)
    session.add(ofn_port)
    session.flush()
    return ofn_port


def del_ofn_port(port_id):
    session = db.get_session()
    try:
        ofn_port = session.query(nec_models.OFNPort).\
          filter_by(port_id=port_id).\
          one()
        session.delete(ofn_port)
        session.flush()
    except exc.NoResultFound:
        LOG.warning("del_ofn_port(): NotFound ofn_port for "
                    "port_id: %s" % port_id)


def get_vifinfo(interface_id):
    session = db.get_session()
    try:
        return session.query(nec_models.VIFInfo).\
          filter_by(interface_id=interface_id).\
          one()
    except exc.NoResultFound:
        return None


def list_vifinfos():
    session = db.get_session()
    return session.query(nec_models.VIFInfo).all()


def add_vifinfo(interface_id, datapath_id, port_no, vlan_id=65535):
    session = db.get_session()
    vif = nec_models.VIFInfo(interface_id, datapath_id, port_no, vlan_id)
    session.add(vif)
    session.flush()
    return vif


def del_vifinfo(interface_id):
    session = db.get_session()
    try:
        vif = session.query(nec_models.VIFInfo).\
          filter_by(interface_id=interface_id).\
          one()
        session.delete(vif)
        session.flush()
    except exc.NoResultFound:
        LOG.warning("del_vifinfo(): NotFound vifinfo for "
                    "interface_id: %s" % interface_id)

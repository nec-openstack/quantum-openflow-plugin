# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import logging
from sqlalchemy.orm import exc

import quantum.db.api as db
import quantum.plugins.nec.db.nec_models as models

LOG = logging.getLogger(__name__)


def initialize(conf):
    options = {'sql_connection': conf.DB}
    LOG.debug("Configure DB: %s" % options)
    db.configure_db(options)


def get_ofn_tenant(tenant_id):
    session = db.get_session()
    try:
        return session.query(models.OFNTenant).\
          filter_by(tenant_id=tenant_id).\
          one()
    except exc.NoResultFound:
        return None


def add_ofn_tenant(ofn_tenant_id, tenant_id):
    session = db.get_session()
    ofntenant = models.OFNTenant(ofn_tenant_id, tenant_id)
    session.add(ofntenant)
    session.flush()
    return ofntenant


def del_ofn_tenant(tenant_id):
    session = db.get_session()
    try:
        ofntenant = session.query(models.OFNTenant).\
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
        return session.query(models.OFNNetwork).\
          filter_by(network_id=network_id).\
          one()
    except exc.NoResultFound:
        return None


def add_ofn_network(ofn_network_id, network_id):
    session = db.get_session()
    ofn_network = models.OFNNetwork(ofn_network_id, network_id)
    session.add(ofn_network)
    session.flush()
    return ofn_network


def del_ofn_network(network_id):
    session = db.get_session()
    try:
        ofn_network = session.query(models.OFNNetwork).\
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
        return session.query(models.OFNPort).\
          filter_by(port_id=port_id).\
          one()
    except exc.NoResultFound:
        return None


def add_ofn_port(ofn_port_id, port_id):
    session = db.get_session()
    ofn_port = models.OFNPort(ofn_port_id, port_id)
    session.add(ofn_port)
    session.flush()
    return ofn_port


def del_ofn_port(port_id):
    session = db.get_session()
    try:
        ofn_port = session.query(models.OFNPort).\
          filter_by(port_id=port_id).\
          one()
        session.delete(ofn_port)
        session.flush()
    except exc.NoResultFound:
        LOG.warning("del_ofn_port(): NotFound ofn_port for "
                    "port_id: %s" % port_id)


def get_ofn_filter(filter_id):
    session = db.get_session()
    try:
        return session.query(models.OFNFilter).\
          filter_by(filter_id=filter_id).\
          one()
    except exc.NoResultFound:
        return None


def add_ofn_filter(ofn_filter_id, filter_id):
    session = db.get_session()
    ofn_filter = models.OFNFilter(ofn_filter_id, filter_id)
    session.add(ofn_filter)
    session.flush()
    return ofn_filter


def del_ofn_filter(filter_id):
    session = db.get_session()
    try:
        ofn_filter = session.query(models.OFNFilter).\
          filter_by(filter_id=filter_id).\
          one()
        session.delete(ofn_filter)
        session.flush()
    except exc.NoResultFound:
        LOG.warning("del_ofn_filter(): NotFound ofn_filter for "
                    "filter_id: %s" % filter_id)


def get_vifinfo(interface_id):
    session = db.get_session()
    try:
        return session.query(models.VIFInfo).\
          filter_by(interface_id=interface_id).\
          one()
    except exc.NoResultFound:
        return None


def list_vifinfos():
    session = db.get_session()
    return session.query(models.VIFInfo).all()


def add_vifinfo(interface_id, datapath_id=None, port_no=None,
                vlan_id=65535, mac=None):
    session = db.get_session()
    vif = models.VIFInfo(interface_id, datapath_id, port_no, vlan_id, mac)
    session.add(vif)
    session.flush()
    return vif


def del_vifinfo(interface_id):
    session = db.get_session()
    try:
        vif = session.query(models.VIFInfo).\
          filter_by(interface_id=interface_id).\
          one()
        session.delete(vif)
        session.flush()
    except exc.NoResultFound:
        LOG.warning("del_vifinfo(): NotFound vifinfo for "
                    "interface_id: %s" % interface_id)


def get_filter(filter_id, network_id):
    session = db.get_session()
    try:
        return session.query(models.Filter).\
          filter_by(uuid=filter_id).\
          filter_by(network_id=network_id).\
          one()
    except exc.NoResultFound:
        return None


def list_filters(network_id):
    session = db.get_session()
    if network_id:
        return session.query(models.Filter).\
          filter_by(network_id=network_id).\
          all()
    else:
        return session.query(models.Filter).all()


def add_filter(network_id, filter_dict):
    session = db.get_session()
    filter = models.Filter(network_id,
                               filter_dict['priority'],
                               filter_dict['action'],
                               filter_dict['condition'].get('in_port', None),
                               filter_dict['condition'].get('src_mac', None),
                               filter_dict['condition'].get('dst_mac', None),
                               filter_dict['condition'].get('src_cidr', None),
                               filter_dict['condition'].get('dst_cidr', None),
                               filter_dict['condition'].get('protocol', None),
                               filter_dict['condition'].get('src_port', None),
                               filter_dict['condition'].get('dst_port', None))
    session.add(filter)
    session.flush()
    return filter


def update_filter(filter_id, network_id, filter_dict):
    session = db.get_session()
    filter = get_filter(filter_id, network_id)
    filter.priority = filter_dict['priority']
    filter.action = filter_dict['action']
    filter.in_port = filter_dict['condition'].get('in_port', None)
    filter.src_mac = filter_dict['condition'].get('src_mac', None)
    filter.dst_mac = filter_dict['condition'].get('dst_mac', None)
    filter.src_cidr = filter_dict['condition'].get('src_cidr', None)
    filter.dst_cidr = filter_dict['condition'].get('dst_cidr', None)
    filter.protocol = filter_dict['condition'].get('protocol', None)
    filter.src_port = filter_dict['condition'].get('src_port', None)
    filter.dst_port = filter_dict['condition'].get('dst_port', None)
    session.merge(filter)
    session.flush()
    return filter


def del_filter(filter_id, network_id):
    session = db.get_session()
    try:
        filter = session.query(models.Filter).\
          filter_by(uuid=filter_id).\
          filter_by(network_id=network_id).\
          one()
        session.delete(filter)
        session.flush()
    except exc.NoResultFound:
        LOG.warning("del_filter(): NotFound filter for "
                    "filter_id: %s" % filter_id)


def get_associated_filters(network_id, port_id):
    session = db.get_session()
    return session.query(models.Filter).\
      filter_by(in_port=port_id).\
      filter_by(network_id=network_id).\
      all()

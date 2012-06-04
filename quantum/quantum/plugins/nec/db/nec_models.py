# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import uuid

from sqlalchemy import Column, String, Integer, ForeignKey
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import relation, object_mapper

from quantum.db.models import BASE, QuantumBase


class OFNTenant(BASE, QuantumBase):
    """Represents a ofnetwork tenant"""
    __tablename__ = 'ofntenants'

    tenant_id = Column(String(255), primary_key=True)
    ofn_tenant_id = Column(String(255), nullable=False)

    def __init__(self, ofn_tenant_id, tenant_id):
        self.ofn_tenant_id = ofn_tenant_id
        self.tenant_id = tenant_id

    def __repr__(self):
        return "<OFNTenant(ofn_tenant_id=%s," % self.ofn_tenant_id + \
                          "tenant_id=%s)>" % self.tenant_id


class OFNNetwork(BASE, QuantumBase):
    """Represents a ofnetwork network"""
    __tablename__ = 'ofnnets'

    network_id = Column(String(255), primary_key=True)
    ofn_network_id = Column(String(255), nullable=False)

    def __init__(self, ofn_network_id, network_id):
        self.ofn_network_id = ofn_network_id
        self.network_id = network_id

    def __repr__(self):
        return "<OFNNetwork(ofn_network_id=%s," % self.ofn_network_id + \
                           "network_id=%s)>" % self.network_id


class OFNPort(BASE, QuantumBase):
    """Represents a ofnetwork port"""
    __tablename__ = 'ofnports'

    port_id = Column(String(255), primary_key=True)
    ofn_port_id = Column(String(255), nullable=False)

    def __init__(self, ofn_port_id, port_id):
        self.ofn_port_id = ofn_port_id
        self.port_id = port_id

    def __repr__(self):
        return "<OFNPort(ofn_port_id=%s," % self.ofn_port_id + \
                        "port_id=%s)>" % self.port_id


class OFNFilter(BASE, QuantumBase):
    """Represents a ofnetwork filter"""
    __tablename__ = 'ofnfilters'

    filter_id = Column(String(255), primary_key=True)
    ofn_filter_id = Column(String(255), nullable=False)

    def __init__(self, ofn_filter_id, filter_id):
        self.ofn_filter_id = ofn_filter_id
        self.filter_id = filter_id

    def __repr__(self):
        return "<OFNFilter(ofn_filter_id=%s," % self.ofn_filter_id + \
                        "filter_id=%s)>" % self.filter_id


class VIFInfo(BASE, QuantumBase):
    """Represents a vifinfo"""
    __tablename__ = 'vifinfo'

    interface_id = Column(String(255), primary_key=True)
    datapath_id = Column(String(255), nullable=False)
    port_no = Column(Integer, nullable=False)
    vlan_id = Column(Integer)
    mac = Column(String(36))

    def __init__(self, interface_id, datapath_id=None, port_no=None,
                 vlan_id=65535, mac=None):
        self.interface_id = interface_id
        self.datapath_id = datapath_id
        self.port_no = port_no
        self.vlan_id = vlan_id
        self.mac = mac

    def __repr__(self):
        return "<VIFInfo(interface_id=%s," % self.interface_id + \
                        "datapath_id=%s," % self.datapath_id + \
                        "port_no=%s," % self.port_no + \
                        "vlan_id=%s," % self.vlan_id +\
                        "mac=%s)>" % self.mac


class Filter(BASE, QuantumBase):
    """Represents a filter"""
    __tablename__ = 'filters'

    uuid = Column(String(255), primary_key=True)
    network_id = Column(String(255), nullable=False)
    priority = Column(Integer, nullable=False)
    action = Column(String(7), nullable=False)
    # condition
    in_port = Column(String(255))
    src_mac = Column(String(31))
    dst_mac = Column(String(31))
    src_cidr = Column(String(31))
    dst_cidr = Column(String(31))
    protocol = Column(String(7))
    src_port = Column(Integer)
    dst_port = Column(Integer)

    def __init__(self, network_id, priority, action,
                 in_port=None, src_mac=None, dst_mac=None,
                 src_cidr=None, dst_cidr=None, protocol=None,
                 src_port=None, dst_port=None):
        self.uuid = str(uuid.uuid4())
        self.network_id = network_id
        self.priority = priority
        self.action = action
        self.in_port = in_port
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.src_cidr = src_cidr
        self.dst_cidr = dst_cidr
        self.protocol = protocol
        self.src_port = src_port
        self.dst_port = dst_port

    def __repr__(self):
        return "<Filter(uuid=%s," % self.uuid + \
                       "network_id=%s," % self.network_id + \
                       "priority=%s," % self.priority + \
                       "action=%s," % self.action + \
                       "in_port=%s," % self.in_port + \
                       "src_mac=%s," % self.src_mac + \
                       "dst_mac=%s," % self.dst_mac + \
                       "src_cidr=%s," % self.src_cidr + \
                       "dst_cidr=%s," % self.dst_cidr + \
                       "protocol=%s," % self.protocol + \
                       "src_port=%s," % self.src_port + \
                       "dst_port=%s>" % self.dst_port

    def dic(self):
        return {"filter": {"id": self.uuid,
                           "action": self.action,
                           "priority": self.priority,
                           "condition": {"in_port": self.in_port,
                                         "src_mac": self.src_mac,
                                         "dst_mac": self.dst_mac,
                                         "src_cidr": self.src_cidr,
                                         "dst_cidr": self.dst_cidr,
                                         "protocol": self.protocol,
                                         "src_port": self.src_port,
                                         "dst_port": self.dst_port}}}

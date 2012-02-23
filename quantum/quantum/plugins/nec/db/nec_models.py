# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import uuid

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, object_mapper

from quantum.db.models import BASE, QuantumBase


class VIFInfo(BASE, QuantumBase):
    """Represents a vifinfo"""
    __tablename__ = 'vifinfo'

    interface_id = Column(String(255), primary_key=True)
    datapath_id = Column(String(255), nullable=False)
    port_no = Column(Integer, nullable=False)
    vlan_id = Column(Integer)

    def __init__(self, interface_id, datapath_id, port_no, vlan_id=65535):
        self.interface_id = interface_id
        self.datapath_id = datapath_id
        self.port_no = port_no
        self.vlan_id = vlan_id

    def __repr__(self):
        return "<VIFInfo(interface_id=%s," % self.interface_id + \
                        "datapath_id=%s," % self.datapath_id + \
                        "port_no=%s," % self.port_no + \
                        "vlan_id=%s)>" % self.vlan_id


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

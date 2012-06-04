#!/bin/bash -ex
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

OFC_HOST=${OFC_HOST:-127.0.0.1}
OVS_BRIDGE=${OVS_BRIDGE:-br-int}


kernel_version=`cat /proc/version | cut -d " " -f3`
sudo apt-get install -y openvswitch-switch openvswitch-datapath-dkms linux-headers-$kernel_version

sudo ovs-vsctl --no-wait -- --if-exists del-br $OVS_BRIDGE
sudo ovs-vsctl --no-wait add-br $OVS_BRIDGE
sudo ovs-vsctl --no-wait set-controller $OVS_BRIDGE tcp:$OFC_HOST
sudo /sbin/ifconfig $OVS_BRIDGE up

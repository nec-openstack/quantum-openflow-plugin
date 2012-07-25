#!/bin/bash -ex
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

if [ -n "$LOCALRC" -a -e "$LOCALRC" ]; then
    . $LOCALRC
fi

OFC_HOST=${OFC_HOST:-127.0.0.1}
OVS_BRIDGE=${OVS_BRIDGE:-br-int}
OVS_INTERFACE=${OVS_INTERFACE:-}
GRE_REMOTE_IPS=${GRE_REMOTE_IPS:-}

kernel_version=`cat /proc/version | cut -d " " -f3`
sudo apt-get install -y openvswitch-switch openvswitch-datapath-dkms linux-headers-$kernel_version

sudo ovs-vsctl --no-wait -- --if-exists del-br $OVS_BRIDGE
sudo ovs-vsctl --no-wait add-br $OVS_BRIDGE
sudo ovs-vsctl --no-wait set-controller $OVS_BRIDGE tcp:$OFC_HOST
if [ -n "$OVS_INTERFACE" ]; then
  	sudo ovs-vsctl --no-wait add-port $OVS_BRIDGE $OVS_INTERFACE
fi
if [ -n "$GRE_REMOTE_IPS" ]; then
    id=0
    for ip in ${GRE_REMOTE_IPS//:/ }
    do
        sudo ovs-vsctl --no-wait add-port $OVS_BRIDGE gre$id -- \
            set Interface gre$id type=gre options:remote_ip=$ip
        id=`expr $id + 1`
    done
fi

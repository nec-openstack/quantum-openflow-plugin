#!/bin/bash -ex
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

LOCALRC=${LOCALRC:-localrc}
OVS_BRIDGE=${OVS_BRIDGE:-br-int}


if [ -e "$LOCALRC" ]; then
    eval $(grep "^OVS_BRIDGE=" $LOCALRC)
    eval $(grep "^OVS_INTERFACE=" $LOCALRC)
    eval $(grep "^GRE_REMOTE_IPS=" $LOCALRC)
fi

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

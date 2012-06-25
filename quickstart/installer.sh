#!/bin/bash -ex
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

CDIR=$(cd $(dirname "$0") && pwd)
DEVSTACK_REPO=http://github.com/openstack-dev/devstack.git
DEVSTACK_DIR=devstack
DEVSTACK_BRANCH=6bedba790250b9b67776645c690d29d58d94ceac

LOCALRC=$CDIR/localrc

$CDIR/scripts/config-cgroup-device-acl.sh

SLICEABLE_PATCH="$CDIR/patches/trema/0001-fixed-create_filter-in-config.cgi.patch" \
    $CDIR/scripts/install-trema-sliceable-switch.sh

LOCALRC=$LOCALRC $CDIR/scripts/install-ovs-as-ofs.sh

[ -f /usr/bin/git ] || sudo apt-get -y install git
git clone $DEVSTACK_REPO $DEVSTACK_DIR
pushd $DEVSTACK_DIR
git checkout $DEVSTACK_BRANCH
git am $CDIR/patches/devstack/0001-support-Quantum-NEC-OpenFlow-Plugin.patch
git am $CDIR/patches/devstack/0002-support-http_proxy.patch
cp $LOCALRC .
./stack.sh
popd

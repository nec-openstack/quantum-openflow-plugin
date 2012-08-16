#!/bin/bash -ex
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

MODE=cc
if [ -n "$1" ]; then
  case "$1" in
      "hv"|"compute")    MODE=hv ;;
      "cc"|"controller") MODE=cc ;;
      *)  echo "Unsupported mode! Supported modes are 'cc' and 'hv'.";
	  exit 1 ;;
  esac
fi

CDIR=$(cd $(dirname "$0") && pwd)
NEC_PLUGIN_DIR=$(dirname "$CDIR")
DEVSTACK_REPO=http://github.com/openstack-dev/devstack.git
DEVSTACK_DIR=devstack
DEVSTACK_BRANCH=6bedba790250b9b67776645c690d29d58d94ceac

if [ "$MODE" = "hv" ]; then
    LOCALRC=$CDIR/localrc-hv
else # MODE = cc
    LOCALRC=$CDIR/localrc
fi

$CDIR/scripts/config-cgroup-device-acl.sh

if [ "$MODE" = "cc" ]; then
    SLICEABLE_PATCH="$CDIR/patches/trema/0001-fixed-create_filter-in-config.cgi.patch" \
	$CDIR/scripts/install-trema-sliceable-switch.sh
fi

LOCALRC=$LOCALRC $CDIR/scripts/install-ovs-as-ofs.sh

[ -f /usr/bin/git ] || sudo apt-get -y install git

if [ ! -e $DEVSTACK_DIR ]; then
    git clone $DEVSTACK_REPO $DEVSTACK_DIR
    pushd $DEVSTACK_DIR
    git checkout $DEVSTACK_BRANCH
    patch -p1 < $CDIR/patches/devstack-support-nec-openflow-plugin.patch
    cp $LOCALRC ./localrc
    popd
fi
pushd $DEVSTACK_DIR
./unstack.sh
NEC_PLUGIN_DIR=$NEC_PLUGIN_DIR ./stack.sh
popd

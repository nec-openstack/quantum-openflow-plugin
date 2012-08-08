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
DEVSTACK_REPO=http://github.com/openstack-dev/devstack.git
DEVSTACK_DIR=devstack
DEVSTACK_BRANCH=0416f332fdbb55a2dbeb68810fa165bdb1e0f4a4

if [ "$MODE" = "hv" ]; then
    LOCALRC=$CDIR/localrc-hv
else # MODE = cc
    LOCALRC=$CDIR/localrc
fi

if [ "$MODE" = "cc" ]; then
    SLICEABLE_PATCH="$CDIR/patches/trema/0001-fixed-create_filter-in-config.cgi.patch" \
	$CDIR/scripts/install-trema-sliceable-switch.sh
fi

[ -f /usr/bin/git ] || sudo apt-get -y install git

if [ ! -e $DEVSTACK_DIR ]; then
    git clone $DEVSTACK_REPO $DEVSTACK_DIR
    pushd $DEVSTACK_DIR
    git checkout $DEVSTACK_BRANCH
    patch -p1 < $CDIR/patches/devstack/support-quantum-nec-openflow-plugin-v2.patch
    patch -p1 < $CDIR/patches/devstack/support-quantum-nec-plugin-get-review-code.patch
    patch -p1 < $CDIR/patches/devstack/fix-dependency.patch
    cp $LOCALRC ./localrc
    popd
fi
pushd $DEVSTACK_DIR
    ./stack.sh
popd

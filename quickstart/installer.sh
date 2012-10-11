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
DEVSTACK_REPO=https://github.com/nec-openstack/devstack-quantum-nec-openflow.git
DEVSTACK_BRANCH=develop
DEVSTACK_DIR=devstack

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
    git clone -b $DEVSTACK_BRANCH $DEVSTACK_REPO $DEVSTACK_DIR
    pushd $DEVSTACK_DIR
    cp $LOCALRC ./localrc
    popd
fi
pushd $DEVSTACK_DIR
    ./stack.sh
popd

#!/bin/bash -ex
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

DEVSTACK_REPO=https://github.com/nec-openstack/devstack-quantum-nec-openflow.git
DEVSTACK_BRANCH=folsom

CDIR=$(cd $(dirname "$0") && pwd)
DEVSTACK_DIR=$CDIR/devstack
CONF_DIR=$DEVSTACK_DIR/samples/nec-openflow

if [ "$1" = "-s" ]; then
    SETUP_ONLY=1
    shift
fi
echo "$1"
case "$1" in
    "hv"|"compute")       LOCALRC=$CONF_DIR/localrc-hv ;;
    "cc"|"controller"|"") LOCALRC=$CONF_DIR/localrc ;;
    *)  echo "Unsupported mode! Supported modes are 'cc' and 'hv'.";
	  exit 1 ;;
esac

[ -x /usr/bin/git ] || sudo apt-get -y install git

if [ ! -e $DEVSTACK_DIR ]; then
    git clone -b $DEVSTACK_BRANCH $DEVSTACK_REPO $DEVSTACK_DIR
    cp $LOCALRC $DEVSTACK_DIR/localrc
fi
if [ -n "$SETUP_ONLY" ]; then
  echo "devstack for NEC OpenFlow plugin is now deployed."
  echo "Customize devstack if required."
  echo "Then run devstack:"
  echo "  cd $DEVSTACK_DIR && ./stack.sh"
  exit 0
fi

cd $DEVSTACK_DIR
./stack.sh
cd $CDIR

#!/bin/bash -ex
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

INSTALLER_DIR=$(cd $(dirname "$0") && pwd)
NEC_PLUGIN_DIR=${INSTALLER_DIR%/quickstart}
QUANTUM_DIR=$NEC_PLUGIN_DIR/quantum
TREMA_DIR=$NEC_PLUGIN_DIR/trema

source "$INSTALLER_DIR/scripts/functions.sh"
source "$INSTALLER_DIR/installerrc"

check_distrib
check_config

. $INSTALLER_DIR/scripts/1-install-nova
set_nova_conf
set_nec_plugin_nova_code
apply_nova_patch
init_nova_db
restart_nova_services

. $INSTALLER_DIR/scripts/2-install-trema-srs
. $INSTALLER_DIR/scripts/3-install-ovs
. $INSTALLER_DIR/scripts/4-install-quantum

if [ -n "$IMAGE_TAR" -o -n "$IMAGE_URL" ]
then
	. $INSTALLER_DIR/scripts/5-register-image
fi
if [ -n "$USER" -a -n "$PROJECT" ]
then
	CREDS_DIR=$INSTALLER_DIR/creds
	. $INSTALLER_DIR/scripts/6-create-project
    modify_create_network_sh
fi

echo "Done."

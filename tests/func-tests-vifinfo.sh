#!/bin/bash -ex

TOP_DIR=$(cd $(dirname "$0") && pwd)
source $TOP_DIR/functions


vif_id="cbebaf45-5d9c-43ab-bb4a-75b85c8ca001"
dpid="0x00000a001"
port_no=1
dpidn="0x00000a002"
port_non=2


create_vifinfo $vif_id $dpid $port_no
update_vifinfo $vif_id $dpidn $port_non

stopstop

delete_vifinfo $vif_id

ok_farm

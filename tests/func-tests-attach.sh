#!/bin/bash -ex

TOP_DIR=$(cd $(dirname "$0") && pwd)
source $TOP_DIR/functions


tenant="tenant001"
net_name="net001"
vif_id="0bebaf45-5d9c-43ab-bb4a-75b85c8ca001"
dpid1="0x000000001"
port_no1=1
dpid2="0x000000002"
port_no2=2

create_net $tenant $net_name
check_slice $net_id created
create_port $tenant $net_id

# check vifinfo
activate_port $tenant $net_id $port_id
plug_iface $tenant $net_id $port_id $vif_id
create_vifinfo $vif_id $dpid1 $port_no1
check_binding $port_id created

update_vifinfo $vif_id $dpid2 $port_no2
check_binding $port_id created

delete_vifinfo $vif_id
check_binding $port_id deleted
unplug_iface $tenant $net_id $port_id

# check plug
create_vifinfo $vif_id $dpid1 $port_no1
plug_iface $tenant $net_id $port_id $vif_id
check_binding $port_id created

unplug_iface $tenant $net_id $port_id
check_binding $port_id deleted
deactivate_port $tenant $net_id $port_id

# check activate
plug_iface $tenant $net_id $port_id $vif_id
activate_port $tenant $net_id $port_id
check_binding $port_id created

deactivate_port $tenant $net_id $port_id
check_binding $port_id deleted
unplug_iface $tenant $net_id $port_id
delete_vifinfo $vif_id

delete_port $tenant $net_id $port_id
delete_net $tenant $net_id
ok_farm

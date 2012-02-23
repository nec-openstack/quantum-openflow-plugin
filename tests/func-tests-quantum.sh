#!/bin/bash -ex

cli="../quantum/bin/cli"
tenant="tenant001"
net="net001"
vif_id="cbebaf45-5d9c-43ab-bb4a-75b85c8ca001"



echo "# create network #"

$cli create_net $tenant $net > ret
grep "^Created a new Virtual Network with ID: " ret
grep "^for Tenant: $tenant" ret
net_id=$(grep "^Created a new Virtual Network with ID: " ret \
         | sed -e "s/^Created a new Virtual Network with ID: //")
echo "net_id: $net_id"
[ ${#net_id} -eq 0 ] && exit 1

$cli list_nets $tenant > ret
grep "Network ID: $net_id" ret

$cli show_net $tenant $net_id > ret
grep "^Network ID: $net_id" ret
grep "^network Name: $net" ret


echo "# rename network #"

$cli rename_net $tenant $net_id ${net}_renamed > ret
grep "^Renamed Virtual Network with ID: $net_id" ret
grep "^for Tenant: $tenant" ret
grep "^new name is: ${net}_renamed" ret

$cli show_net $tenant $net_id > ret
grep "^Network ID: $net_id" ret
grep "^network Name: ${net}_renamed" ret


echo "# create port #"

$cli create_port $tenant $net_id > ret
grep "^Created new Logical Port with ID: " ret
grep "^on Virtual Network: $net_id" ret
grep "^for Tenant: $tenant" ret
port_id=$(grep "^Created new Logical Port with ID: " ret \
          | sed -e "s/^Created new Logical Port with ID: //")
echo "port_id: $port_id"
[ ${#port_id} -eq 0 ] && exit 1

$cli list_ports $tenant $net_id > ret
grep "Logical Port: $port_id" ret

$cli set_port_state $tenant $net_id $port_id ACTIVE > ret
grep "^Updated state for Logical Port with ID: $port_id" ret
grep "^new state is: ACTIVE" ret
grep "^on Virtual Network: $net_id" ret
grep "^for tenant: $tenant" ret

$cli show_port $tenant $net_id $port_id > ret
grep "^Logical Port ID: $port_id" ret
grep "^administrative State: ACTIVE" ret
grep "^interface: <none>" ret
grep "^on Virtual Network: $net_id" ret
grep "^for Tenant: $tenant" ret


echo "# plug port #"

$cli plug_iface $tenant $net_id $port_id $vif_id > ret
grep "^Plugged interface $vif_id" ret
grep "^into Logical Port: $port_id" ret
grep "^on Virtual Network: $net_id" ret
grep "^for Tenant: $tenant" ret

$cli show_port $tenant $net_id $port_id > ret
grep "^Logical Port ID: $port_id" ret
grep "^administrative State: ACTIVE" ret
grep "^interface: $vif_id" ret
grep "^on Virtual Network: $net_id" ret
grep "^for Tenant: $tenant" ret


echo "# created, press ENTER to continue ... #"
read hoge


echo "# unplug port #"

$cli unplug_iface $tenant $net_id $port_id > ret
grep "^Unplugged interface from Logical Port: *$port_id" ret
grep "^on Virtual Network: $net_id" ret
grep "^for Tenant: $tenant" ret

$cli show_port $tenant $net_id $port_id > ret
grep "^Logical Port ID: $port_id" ret
grep "^administrative State: ACTIVE" ret
grep "^interface: <none>" ret
grep "^on Virtual Network: $net_id" ret
grep "^for Tenant: $tenant" ret


echo "# delete port #"

$cli delete_port $tenant $net_id $port_id > ret
grep "^Deleted Logical Port with ID: $port_id" ret
grep "^on Virtual Network: $net_id" ret
grep "^for Tenant: $tenant" ret

$cli list_ports $tenant $net_id > ret
grep "Logical Port: $port_id" ret && exit 1 || echo "ok"


echo "# delete network #"

$cli delete_net $tenant $net_id > ret
grep "Deleted Virtual Network with ID: $net_id" ret
grep "^for Tenant $tenant" ret

$cli list_nets $tenant > ret
grep "Network ID: $net_id" ret && exit 1 || echo "ok"


rm -f ret
echo "# OK #"

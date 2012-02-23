#!/bin/bash -ex

dir="${0%/*}"
cli="../nova/vifinfo_cli.py -v --logfile=$dir/vifinfo_cli.log"
vif_id="2920bbd3-a678-471a-ad9d-b043c202f8d5"
vif_dpid="0x00000a001"
vif_port=1
vif_dpid_n="0x00000a002"
vif_port_n=2



echo "# create vifinfo #"

$cli list_vifinfos > ret
grep "^Interface ID: $vif_id" ret && exit 1 || echo "ok"

$cli create_vifinfo $vif_id $vif_dpid $vif_port > ret
grep "^Interface ID: $vif_id" ret

$cli list_vifinfos > ret
grep "^Interface ID: $vif_id" ret

$cli show_vifinfo $vif_id > ret
grep "^Interface ID: $vif_id" ret
grep "Datapath ID: $vif_dpid" ret
grep "OFPort No: *$vif_port" ret


echo "# modify vifinfo #"

$cli update_vifinfo $vif_id $vif_dpid_n $vif_port_n > ret

$cli show_vifinfo $vif_id > ret
grep "^Interface ID: $vif_id" ret
grep "Datapath ID: $vif_dpid_n" ret
grep "OFPort No: *$vif_port_n" ret


echo "# created, press ENTER to continue ... #"
read hoge


echo "# delete vifinfo #"

$cli list_vifinfos > ret
grep "^Interface ID: $vif_id" ret

$cli delete_vifinfo $vif_id > ret

$cli list_vifinfos > ret
grep "^Interface ID: $vif_id" ret && exit 1 || echo "ok"


rm -f ret
echo "# OK #"

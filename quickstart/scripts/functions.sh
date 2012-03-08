# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

check_distrib() {
	if [ "x`lsb_release -d -s`" != "xUbuntu 11.04" ]
	then
		echo "Error: Sorry, try this script on Ubuntu 11.04."
		exit 1
	fi
}

check_config() {
	for i in MYSQL_PASS NDB_PASS QDB_NAME QDB_USER QDB_PASS BRIDGE
	do
		eval val'=$'$i
		[ -z $val ] && echo "Error: set $i." && exit 1
	done
	if [ -z "$HOST_IP" ]
	then
		HOST_IP=`LC_ALL=C /sbin/ifconfig eth0 | \
				grep -m 1 'inet addr:' | \
				cut -d: -f2 | \
				awk '{print $1}'`
		echo "Note: use eth0 IP address $HOST_IP as HOST_IP."
	fi
}

set_nova_conf() {
	dir="$INSTALLER_DIR"
	base="$dir/nova.conf.base"
	filled="$dir/nova.conf"
	target="/etc/nova/nova.conf"
	if ! [ -f $base ]
	then
		echo "Error: no nova.conf.base."
		exit 1
	fi
	sudo mkdir -p /etc/nova
	[ -f $target ] && sudo mv $target $target.bak
	if ! [ -f $filled ]
	then
		sed -e "s/@BRIDGE@/$BRIDGE/g" \
		    -e "s/@NDB_PASS@/$NDB_PASS/g" \
		    -e "s/@HOST_IP@/$HOST_IP/g" \
		    "$base" > $filled
	fi
	sudo ln -sb $filled $target
}

set_nec_plugin_nova_code() {
	src="$NEC_PLUGIN_DIR"
	target="/usr/lib/python2.7/dist-packages/nova/virt/libvirt/nec"
	if ! [ -d "$target" ]
	then
		sudo ln -sf $src/nova "$target"
	fi
}

apply_nova_patch() {
	# fix nova-network for quantum api v1.0
	sudo patch -p 1 -d /usr/share/pyshared < $INSTALLER_DIR/patches/nova-network.patch
}

init_nova_db() {
	sudo nova-manage --flagfile=/etc/nova/nova.conf db sync
}

restart_nova_services() {
	ps aux | grep '^root.*dnsmasq' && sudo killall dnsmasq
	sudo stop nova-network || echo "not running..."
	sudo start nova-network
	sudo stop nova-compute || echo "not running..."
	sudo start nova-compute
	sudo stop nova-api || echo "not running..."
	sudo start nova-api
	sudo stop nova-scheduler || echo "not running..."
	sudo start nova-scheduler
}

modify_create_network_sh() {
	dir="$INSTALLER_DIR"
	sed -e "4aPROJECT=\"$PROJECT\"" \
	    -e "4aBRIDGE=\"$BRIDGE\"" \
	    -e "4aTREMA_DIR=\"$TREMA_DIR\"" \
	    -e "4aQUANTUM_DIR=\"$QUANTUM_DIR\"" \
	    "$dir/scripts/7-create-network" > "$dir/create-private-network.sh"
	chmod +x "$dir/create-private-network.sh"
}

#!/bin/bash -ex

TOP_DIR=$(cd $(dirname "$0") && pwd)
source $TOP_DIR/functions


# parameter
ftype=${1:-1}
tenant=${2:-tenant001}
net_id=${3:-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa}
port_id=${4:-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb}
src_cidr=${5:-192.168.1.0/24}
dst_cidr=${6:-192.168.2.0/24}
src_mac=${7:-00:00:01:00:00:01}
dst_mac=${8:-00:00:02:00:00:02}



# A. api test
if [ "$ftype" -eq 1 ]
then
	filter_rules=('"priority": 1000' '"action": "DROP"')
	filter_rules_n=('"priority": 1001' '"action": "ACCEPT"')
elif [ "$ftype" -eq 2 ]
then
	filter_rules=('"priority": 1002' '"action": "ACCEPT"' \
		"\"in_port\": \"$port_id\"" \
		"\"src_mac\": \"00:00:00:00:00:01\"" "\"dst_mac\": \"00:00:00:00:00:02\"" \
		"\"src_cidr\": \"192.168.1.1/32\"" "\"dst_cidr\": \"192.168.2.0/24\"" \
		"\"protocol\": \"TCP\"" \
		"\"src_port\": 10001" "\"dst_port\": 10002")
	filter_rules_n=('"priority": 1003' '"action": "ACCEPT"' \
		"\"in_port\": \"$port_id\"" \
		"\"src_mac\": \"00:00:00:00:00:11\"" "\"dst_mac\": \"00:00:00:00:00:12\"" \
		"\"src_cidr\": \"192.168.1.0/24\"" "\"dst_cidr\": \"192.168.12.0/24\"" \
		"\"protocol\": \"UDP\"" \
		"\"src_port\": 10011" "\"dst_port\": 10012")

# B. network specified
elif [ "$ftype" -eq 3 ]
then
	filter_rules=('"priority": 2000' '"action": "DROP"')
elif [ "$ftype" -eq 4 ]
then
	filter_rules=('"priority": 2001' '"action": "ACCEPT"' \
		"\"protocol\": \"ARP\"")
elif [ "$ftype" -eq 5 ]
then
	filter_rules=('"priority": 2002' '"action": "ACCEPT"' \
		"\"protocol\": \"ICMP\"")
elif [ "$ftype" -eq 6 ]
then
	filter_rules=('"priority": 2003' '"action": "ACCEPT"' \
		"\"protocol\": \"TCP\"" "\"dst_port\": 22")
elif [ "$ftype" -eq 7 ]
then
	filter_rules=('"priority": 2004' '"action": "ACCEPT"' \
		"\"protocol\": \"TCP\"")
elif [ "$ftype" -eq 8 ]
then
	filter_rules=('"priority": 2005' '"action": "ACCEPT"' \
		"\"protocol\": \"UDP\"" "\"dst_port\": 33")
elif [ "$ftype" -eq 9 ]
then
	filter_rules=('"priority": 2006' '"action": "ACCEPT"' \
		"\"protocol\": \"UDP\"")

# C. port specified (antispoof)
elif [ "$ftype" -eq 10 ]
then
	filter_rules=('"priority": 3000' '"action": "DROP"')
elif [ "$ftype" -eq 11 ]
then
	filter_rules=('"priority": 3001' '"action": "ACCEPT"' \
		"\"in_port\": \"$port_id\"" "\"src_mac\": \"$src_mac\"" \
		"\"protocol\": \"ARP\"")
elif [ "$ftype" -eq 12 ]
then
	filter_rules=('"priority": 3002' '"action": "ACCEPT"' \
		"\"in_port\": \"$port_id\"" "\"src_mac\": \"$src_mac\"" \
		"\"protocol\": \"ICMP\"")
elif [ "$ftype" -eq 13 ]
then
	filter_rules=('"priority": 3003' '"action": "ACCEPT"' \
		"\"in_port\": \"$port_id\"" "\"src_mac\": \"$src_mac\"" \
		"\"protocol\": \"TCP\"" "\"dst_port\": 22")
elif [ "$ftype" -eq 14 ]
then
	filter_rules=('"priority": 3004' '"action": "ACCEPT"' \
		"\"in_port\": \"$port_id\"" "\"src_mac\": \"$src_mac\"" \
		"\"protocol\": \"TCP\"")
elif [ "$ftype" -eq 15 ]
then
	filter_rules=('"priority": 3005' '"action": "ACCEPT"' \
		"\"in_port\": \"$port_id\"" "\"src_mac\": \"$src_mac\"" \
		"\"protocol\": \"UDP\"" "\"dst_port\": 33")
elif [ "$ftype" -eq 16 ]
then
	filter_rules=('"priority": 3011' '"action": "ACCEPT"' \
		"\"in_port\": \"$port_id\"" "\"src_mac\": \"$src_mac\"" \
		"\"protocol\": \"UDP\"")

# template:
#	filter_rules=('"priority": 1' '"action": "ACCEPT"' \
#		"\"in_port\": \"$port_id\"" \
#		"\"src_mac\": \"$src_mac\"" "\"dst_mac\": \"$dst_mac\"" \
#		"\"src_cidr\": \"$src_cidr\"" "\"dst_cidr\": \"$dst_cidr\"" \
#		"\"protocol\": \"TCP\"" \
#		"\"src_port\": 10001" "\"dst_port\": 10002")
fi


cli="curl -s -S"
path="http://$quantum_server/v1.0/tenants/$tenant/networks/$net_id/filters"
ctype="Content-type: application/json"


if [ "$ftype" -eq 0 ]
then
	list_filters
	exit 0
fi

create_filter "$tenant" "$net_id" "${filter_rules[@]}"

if [ -n "$filter_rules_n" ]
then
	update_filter "$tenant" "$net_id" "$filter_id" "${filter_rules_n[@]}"
fi

stopstop

delete_filter "$filter_id"

ok_farm

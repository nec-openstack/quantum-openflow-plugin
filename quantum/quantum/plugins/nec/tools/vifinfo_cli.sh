#!/bin/bash

_usage() {
        cat << END_usage
Usage: ./vifinfo_cli.sh [OPTIONS] <command> [args]

Options:
  -h, --help            show this help message and exit
  -H HOST, --host=HOST  ip address of api host
  -p PORT, --port=PORT  api poort

Commands:
    create <vif_id> <datapath_id> <port_no> [vlan_id]
    update <vif_id> <datapath_id> <port_no> [vlan_id]
    get <vif_id>
    delete <vif_id>
END_usage
}

check_args() {
    if [ -z "$subcmd" ]; then
        echo "Error: no command."
        _usage
        exit 1
    fi
    if [ -z "$vif_id" ]; then
        echo "Error: no vif_id."
        _usage
        exit 1
    fi
    if [ "x$subcmd" == "xcreate" -o "x$subcmd" == "xupdate" ]; then
        if [ -z "$datapath_id" ]; then
            echo "Error: no datapath_id."
            _usage
            exit 1
        fi
        if [ -z "$port_no" ]; then
            echo "Error: no port_no."
            _usage
            exit 1
        fi
    fi
}

cli() {
    curl -s -S -H "Content-type: application/json" "$@"
}

modify_body() {
    _vif_id=$1
    _datapath_id=$2
    _port_no=$3
    _vlan_id=$4

    if [ -n "$_vlan_id" ]; then
        BODY="{\"vifinfo\": {\"interface_id\": \"$_vif_id\",\
                             \"ofs_port\": {\"datapath_id\": \"$_datapath_id\",\
                                            \"port_no\": \"$_port_no\",\
                                            \"vlan_id\": \"$_vlan_id\" }}}"
    else
        BODY="{\"vifinfo\": {\"interface_id\": \"$_vif_id\",\
                             \"ofs_port\": {\"datapath_id\": \"$_datapath_id\",\
                                            \"port_no\": \"$_port_no\"}}}"
    fi
}


# check curl
if ! which curl ; then
    echo -n "The program 'curl' is currently not installed.  "
    echo "You can install it by typing: sudo apt-get install curl"
    exit 1
fi

# defaults
QUANTUM_HOST=${QUANTUM_HOST:-127.0.0.1}
QUANTUM_PORT=${QUANTUM_PORT:-9696}

# parse option 
while [ "x${1::1}" = "x-" ]; do
    case "$1" in
    "-h"|"--help")
        _usage
        exit 0
    ;;
    "-H"|"--host")
        QUANTUM_HOST=$2
        shift 2
    ;;
    "-p"|"--port")
        QUANTUM_PORT=$2
        shift 2
    ;;
    *)
        echo "Error: unknown option [$1]."
        _usage
        exit 1
    ;;
    esac
done
VIFINFOS_PATH="http://$QUANTUM_HOST:$QUANTUM_PORT/v1.1/extensions/nec/vifinfos"

# load args
subcmd=$1
vif_id=$2
datapath_id=$3
port_no=$4
vlan_id=$5
check_args

# exec command
case "$subcmd" in
"create")
    modify_body $vif_id $datapath_id $port_no $vlan_id
    cli -d "$BODY" "$VIFINFOS_PATH"
;;
"update")
    modify_body $vif_id $datapath_id $port_no $vlan_id
    cli -X PUT -d "$BODY" "$VIFINFOS_PATH/$vif_id"
;;
"get")
    ret=$(cli "$VIFINFOS_PATH/$vif_id" | sed -e "s/[{}]/\n/g" -e "s/, /\n/g")
    echo "$ret" | grep "\"interface_id\":" | sed -e "s/\"//g"
    echo "$ret" | grep "\"datapath_id\":" | sed -e "s/\"//g"
    echo "$ret" | grep "\"port_no\":" | sed -e "s/\"//g"
    echo "$ret" | grep "\"vlan_id\":" | sed -e "s/\"//g"
;;
"delete")
    cli -X DELETE "$VIFINFOS_PATH/$vif_id"
;;
*)
    echo "Error: unknown action [$action]."
    _usage
    exit 1
;;
esac

exit 0

#!/bin/bash -ex
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

if ! [ -f /etc/libvirt/qemu.conf ]; then
    sudo apt-get -y install libvirt-bin
fi

if ! grep -q "^[^#]*/dev/net/tun" /etc/libvirt/qemu.conf; then
    sudo su -c 'cat >> /etc/libvirt/qemu.conf << END
cgroup_device_acl = [
    "/dev/null", "/dev/full", "/dev/zero",
    "/dev/random", "/dev/urandom",
    "/dev/ptmx", "/dev/kvm", "/dev/kqemu",
    "/dev/rtc", "/dev/hpet", "/dev/net/tun",
]
END
'
    sudo service libvirt-bin restart
fi

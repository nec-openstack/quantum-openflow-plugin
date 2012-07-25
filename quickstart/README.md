Quick Start Installer
=====================


What is Quick Start Installer?
------------------------------

Quick Start Installer is a script to build an OpenStack environment with
this Plugin in one machine.  This installer installs and configures all
services that the Quantum NEC OpenFlow Plugin needs.
You can get a trial environment by one command!

Note: From the Essex version of this installer use [Devstack][devstack].


Restrictions
------------

* This installer DO NOT support OS installation.
  Install and setup OS by yourself (setup network, sudo, etc.).
* Supported distribution is Ubuntu 12.04.
* Use MySQL Database.
* Run this installer as a regular user with sudo privileges.


Target Softwares
----------------

* Nova (version Essex)
* Quantum (version Essex) with this plugin
* Trema and Sliceable Switch
* Open vSwitch (deb package)


Installation Modes
------------------

This installer supports following modes:

* **All-In-One** : Run OpenStack+OpenFlow on a single machine. See below.
* **Multi-Node** : Setup a multi-node cluster which consists of
  one cloud controller and several compute nodes.
  See [README-multinode.md][quickstart-multi] for details.

All-In-One (Single node)
------------------------

The instruction below describes how to install OpenStack with NEC OpenFlow plugin
for a single machine. If you would like to install OpenStack with multiple physical
machines, see [README-multinode.md][quickstart-multi].


### Configurations

Configure `quickstart/localrc'.  Set the following parameters:

* HOST_IP: (Option) IP Address of the target HOST
  (If HOST_IP is not specified, the installer use eth0's IP address.)
* _PASSWD: Password for all components

See [Devstack][devstack] for more information.


### Run Installer

Run `installer.sh', and wait...

        $ ./installer.sh

After installation has finished, check console output and log files.
The log files can be found at:

* Nova, Quantum, etc.: /opt/stack/logs/
* Trema:   /tmp/trema/log/


Test VM Launch
--------------

1. Load nova related environment variables.

        $ source quickstart/devstack/openrc

2. Launch VM.
   e.g.:

        $ nova boot --image 450b13ca-c9d1-4990-a736-55e761c6c505 --flavor 1 servera

3. Check Status

        $ nova list

4. Ping, SSH, etc...  Enjoy!

[devstack]: http://devstack.org/
[quickstart-single]: https://github.com/nec-openstack/quantum-openflow-plugin/blob/master/quickstart/README.md
[quickstart-multi]: https://github.com/nec-openstack/quantum-openflow-plugin/blob/master/quickstart/README-multinode.md

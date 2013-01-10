Quick Start Installer
=====================

Previously our quick start installer really installed the OpenStack,
but **NOW this is a thin wrapper of [DevStack with NEC OpenFlow plugin support][devstack-nec-openflow]**.
There are no difference if you use [devstack][devstack-nec-openflow] directly.

Tested platform
---------------

* Ubuntu 12.04 installed machine
* MySQL Database

Installation Modes
------------------

This installer supports following modes:

* **All-In-One** : Run OpenStack+OpenFlow on a single machine. See below.
* **Multi-Node** : Setup a multi-node cluster which consists of
  one cloud controller and several compute nodes.

All-In-One (Single node)
------------------------

The instruction below describes how to install OpenStack with NEC OpenFlow plugin
for a single machine.

## Configurations

Deploy devstack for NEC OpenFlow plugin.

        $ ./installer.sh -s

Configure `devstack/localrc'.
Please see [README][devstack-readme] of devstack with NEC OpenFlow pluign support
for the configuration details.

## Run Installer

Run `installer.sh', and wait... It executes stack.sh inside.

        $ ./installer.sh

or

        $ cd devstack
        $ ./stack.sh

After installation has finished, check console output and log files.
The log files can be found at:

* Nova, Quantum, etc.: /opt/stack/logs/
* Trema:   /tmp/trema/log/


Multi-Node setup
----------------

## Get devstack and prepare localrc (configuartion file)

On the controller node

  $ ./installer.sh -s cc

On the compute nodes

  $ ./installer.sh -s hv

## Configurations

Please see [README][devstack-readme] of devstack with NEC OpenFlow pluign support
for the configuration details.

## Start OpenStack and OpenFlow controller

On the controller node

  $ ./installer.sh cc

On the compute nodes

  $ ./installer.sh hv

Test VM Launch
--------------

1. Load nova related environment variables.

        $ source devstack/openrc

2. Launch VM.
   e.g.:

        $ nova boot --image tty-quantum --flavor 1 server1

3. Check Status

        $ nova list

4. Ping, SSH, etc...  Enjoy!

[devstack]: http://devstack.org/
[devstack-nec-openflow]: https://github.com/nec-openstack/devstack-quantum-nec-openflow/tree/folsom
[devstack-readme]: https://github.com/nec-openstack/devstack-quantum-nec-openflow/blob/folsom/README.md

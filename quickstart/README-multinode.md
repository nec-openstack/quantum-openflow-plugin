Quick Start Installer with Multi-Node
=====================================

Here is how to install OpenStack with NEC OpenFlow plugin into multiple physical machines.


Prerequisites
--------------------

See [README.md][quickstart-single] about the prerequisites and restrictions.


Configure Cluster Controller
------------------------------

## Configurations

Configure `quickstart/localrc'.  Set the following parameters:

* **HOST_IP**: (Option) IP Address of the target HOST
  (If HOST_IP is not specified, the installer use eth0's IP address.)
* **_PASSWD**: Password for all components
* **OVS_INTERFACE**: Uncomment the line and set a physical network interface name
  (e.g., eth1) connected to an OpenFlow enabled network.
  The interface specified in OVS_INTERFACE will be attached to an Open vSwitch bridge
  (named as OVS_BRIDGE) during the installation. When you use tunneling like GRE
  to connect to other nodes, comment out this line (or set an empty value).

See [Devstack][devstack] for more information.

## Run Installer

Run the install script and wait...

        $ ./installer.sh cc

After installation has finished, check console output and log files.
The log files can be found at:

* Nova, Quantum, etc.: /opt/stack/logs/
* Trema:   /tmp/trema/log/


Configure Compute Nodes
------------------------------

On a compute node, only nova-compute will be setup.

## Configurations

Configure `quickstart/localrc-hv'. (Note that the name of the configuration
file ends with `-hv'.) Set the following parameters:

* **CC_HOST**: IP Address of the Cluster Controller.
* **_PASSWD**: Password for all components
* **OVS_INTERFACE**: A physical network interface name
  (e.g., eth1) connected to an OpenFlow enabled network.
  The interface specified in OVS_INTERFACE will be attached to an Open vSwitch bridge
  (named as OVS_BRIDGE) during the installation. When you use tunneling like GRE
  to connect to other nodes, comment out this line (or set an empty value).

See [Devstack][devstack] for more information.

## Run Installer

Run the install script and wait...

        $ ./installer.sh hv

After installation has finished, check console output and log files.
The log files can be found at:

* Nova etc.: /opt/stack/logs/


Test VM Launch
--------------------

Typically you will run the following commands on the cluster controller.

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

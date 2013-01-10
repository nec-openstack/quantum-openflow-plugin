Quantum NEC OpenFlow Plugin (Essex version)
===========================================
A Quantum Plugin for an OpenFlow enabled Network.

The plugin in this repository can be used with **Essex** version of OpenStack Quantum.
**Folsom** version of the plugin is available in the main Quantum distribution.
You can get it from https://launchpad.net/quantum/+download or Ubuntu/Fedora packages.


Introduction
------------

The Quantum NEC OpenFlow Plugin maps L2 logical networks on Quantum to
L2 networks virtualized on an OpenFlow enabled network.
An OpenFlow Controller (OFC) provides L2 network isolation without VLAN,
and this plugin controls the OFC through a REST API.
Two OFC implementations have this API for now:

* Trema with Trema App - Sliceable Switch (OSS)
* ProgrammableFlow Controller with REST API (NEC Commercial Product)

The NEC VIF Driver, to collaborate with OpenStack Nova, informs the OFC
of a VIF - OpenFlow Port mapping via Quantum NEC Extension API (vifinfo),
so that the OFC is automatically configured right after VM deployed.

Currently, this plugin co-works with Essex version of OpenStack Nova
and Quantum.


Related Projects
----------------

* Quantum: https://github.com/openstack/quantum
* OpenStack: http://www.openstack.org
* Trema: http://trema.github.com/trema
* Trema App - Sliceable Switch:
  https://github.com/trema/apps/tree/master/sliceable_switch



Requirements
------------

* Essex version of OpenStack Nova and Quantum
* OpenFlow Controller: Trema with Sliceable Switch,
  ProgrammableFlow Controller with REST API, or an OFC that
  has the same functionalities and REST API as Sliceable Switch has.
  For details see the implementation of Sliceable Switch
  (https://github.com/trema/apps/tree/master/sliceable_switch).
* OpenFlow Switch: Open vSwitch and/or physical switch supported by the OFC.
  You have to create a Network by connecting each OpenFlow switch including
  Open vSwitch on hypervisor node(s) with an exclusive line or GRE tunneling.


Directory Layout
----------------

    quantum-openflow-plugin/
        quantum/                   ... code for Quantum server
            etc/                   ... plugin config
            quantum/extentions/    ... NEC Extensions
            quantum/plugins/nec/   ... Quantum NEC OpenFlow Plugin
                drivers/           ... Drivers for OpenFlow Controller
                nova/              ... VIF/IF driver for Nova
        quickstart/                ... QuickStart Installer


Installations
-------------

We provide a quick-start installer which installs and configures Nova,
Quantum and Trema on one machine.  If you are not familiar with Nova or Trema,
please try the quick-start installer or refer to the scripts in the quick-start
installer.
See [Quick Start Installer][quick-start] for more information.
[quick-start]: https://github.com/nec-openstack/quantum-openflow-plugin/blob/master/quickstart/README.md

With Quick Start Installer, you can build an OpenStack+OpenFlow All-in-One environment
as follows:

        $ git clone https://github.com/nec-openstack/quantum-openflow-plugin.git
        $ cd quantum-openflow-plugin/quickstart
        $ ./installer.sh

NOTE: You can see web GUI information at the last message of this installer.


License&Terms
-------------

Copyright (C) 2012 NEC Corporation

This software is licensed under the [Apache License, Version 2.0][Apache].
[Apache]: http://www.apache.org/licenses/LICENSE-2.0

THIS SOFTWARE IS DISTRIBUTED WITHOUT SUPPORT AND ANY WARRANTY OF
NEC Corporation; WITHOUT EVEN THE IMPLIED WARRANTY OF MERCHANTABILITY OR
FITNESS FOR A PARTICULAR PURPOSE.

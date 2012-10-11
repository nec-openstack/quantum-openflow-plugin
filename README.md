Quantum NEC OpenFlow Plugin
===========================
A Quantum Plugin for an OpenFlow enabled Network.

The plugin for Quantum Folsom is available in the main Quantum distribution.

**For more details, see http://wiki.openstack.org/Quantum-NEC-OpenFlow-Plugin, 
which describes the design and how to install and configure.**


Introduction
------------

The Quantum NEC OpenFlow Plugin maps L2 logical networks on Quantum to
L2 networks virtualized on an OpenFlow enabled network.
An OpenFlow Controller (OFC) provides L2 network isolation without VLAN,
and this plugin controls the OFC through a REST API.
Two OFC implementations have this API for now:

* Trema with Trema App - Sliceable Switch (OSS)
* ProgrammableFlow Controller with REST API (NEC Commercial Product)



Related Projects
----------------

* Quantum: https://github.com/openstack/quantum, http://wiki.openstack.org/Quantum
* OpenStack: http://www.openstack.org
* Trema: http://trema.github.com/trema
* Trema App - Sliceable Switch:
  https://github.com/trema/apps/tree/master/sliceable_switch


License&Terms
-------------

Copyright (C) 2012 NEC Corporation

This software is licensed under the [Apache License, Version 2.0][Apache].
[Apache]: http://www.apache.org/licenses/LICENSE-2.0

THIS SOFTWARE IS DISTRIBUTED WITHOUT SUPPORT AND ANY WARRANTY OF
NEC Corporation; WITHOUT EVEN THE IMPLIED WARRANTY OF MERCHANTABILITY OR
FITNESS FOR A PARTICULAR PURPOSE.

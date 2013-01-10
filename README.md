Quantum NEC OpenFlow Plugin
===========================
A Quantum Plugin for an OpenFlow enabled Network. It is now a part of OpenStack Quantum.

Homepage: http://wiki.openstack.org/Quantum-NEC-OpenFlow-Plugin

How to get
----------

### Folsom or later
  * Quantum mainline : https://github.com/openstack/quantum.git
  * Ubuntu or Fedora packages
  * Customized version : https://github.com/nec-openstack/quantum

### Essex : **essex** branch
Available at https://github.com/nec-openstack/quantum-openflow-plugin/tree/essex

    git clone -b essex https://github.com/nec-openstack/quantum-openflow-plugin.git

### Diablo : **diablo** branch

    git clone -b diablo https://github.com/nec-openstack/quantum-openflow-plugin.git

### Diablo with packet filtering feature : **diablo-filter** branch
This version has an advanced feature of packet filtering in OpenFlow network.
It leverages the packet filtering feature in Trema Sliceable Switch.

    git clone -b diablo-filter https://github.com/nec-openstack/quantum-openflow-plugin.git

Related Projects
----------------

* Quantum: https://github.com/openstack/quantum
* OpenStack: http://www.openstack.org
* Trema: http://trema.github.com/trema
* Trema App - Sliceable Switch:
  https://github.com/trema/apps/tree/master/sliceable_switch

License & Terms
---------------

Copyright (C) 2012 NEC Corporation

This software is licensed under the [Apache License, Version 2.0][Apache].
[Apache]: http://www.apache.org/licenses/LICENSE-2.0

THIS SOFTWARE IS DISTRIBUTED WITHOUT SUPPORT AND ANY WARRANTY OF
NEC Corporation; WITHOUT EVEN THE IMPLIED WARRANTY OF MERCHANTABILITY OR
FITNESS FOR A PARTICULAR PURPOSE.

Manual Installation Guide
=========================
This guide provides how to install and configure the Quantum NEC OpenFlow
Plugin, Nova, Open vSwitch, Trema and Sliceable Routing Switch.


Requirements
------------

* Diablo version of OpenStack Nova and Quantum
* Trema and Trema App - Sliceable Routing Switch
* Open vSwitch


Installations
-------------

### Quantum

Download the Quantum Diablo version and this plugin.
Then copy the plugin into the Quantum directory.
e.g.:

        $ sudo apt-get install git-core
        $ git clone https://github.com/nec-openstack/quantum-openflow-plugin.git
        $ wget http://launchpad.net/quantum/diablo/2011.3/+download/quantum-2011.3.tar.gz
        $ tar xf quantum-2011.3.tar.gz
        $ cp -ir quantum-openflow-plugin/quantum/* quantum-2011.3/

Install a database engine supported by sqlalchemy.
(You can use the same database engine for another OpenStack component.)
e.g. install MySQL:

        $ sudo apt-get install mysql-server

### OpenStack Nova

Install OpenStack Nova Diablo version and other OpenStack components you need.
You have several ways to install OpenStack Components.
(For details see: http://docs.openstack.org/)
e.g. install OpenStack Nova and Glance with deb packages:

        $ sudo apt-get install python-software-properties
        $ sudo add-apt-repository ppa:openstack-release/2011.3
        $ sudo apt-get update
        $ sudo apt-get install python-greenlet python-mysqldb nova-common python-nova rabbitmq-server nova-api nova-scheduler nova-compute nova-network glance

Install the NEC VIF driver on nova-compute node(s).
e.g. link the NEC VIF driver to python Nova libraries:

        $ sudo ln -s quantum-openflow-plugin/nova /usr/lib/python2.7/dist-packages/nova/virt/libvirt/nec


### OpenFlow Controller (Trema)

Install prerequisite packages for Trema and REST API.

        $ sudo apt-get install gcc make ruby ruby-dev irb sudo file libpcap-dev libsqlite3-dev sqlite3 apache2-mpm-prefork libjson-perl libdbi-perl libdbd-sqlite3-perl
        $ git clone https://github.com/trema/trema.git trema
        $ git clone https://github.com/trema/apps.git apps

NOTE: These repositories are active.
The process of installations and configurations could be changed.
Check the following links:

* Trema: http://trema.github.com/trema/
* Slicesable Routing Switch:
  https://github.com/trema/apps/tree/master/sliceable_switch

Then build Trema, "topology" and "Slicesable Routing Switch".

        $ cd trema
        $ ./build.rb
        $ cd ../apps/topology
        $ make
        $ cd ../apps/sliceable_routing_switch
        $ make

### OpenFlow Switch (Open vSwitch)

Install Open vSwitch on nova-compute node(s) and nova-network node(s).
e.g. install Open vSwitch with Dynamic Module Support as the following:

        $ sudo apt-get install openvswitch-switch openvswitch-datapath-dkms


Configurations
--------------

### Quantum

At Quantum Server, put the plugin to the current quantum plugin.
Edit quantum-2011.3/quantum/plugins.ini and change the provider to be:

        provider = quantum.plugins.nec.nec_plugin.NECPlugin

Create a database for the plugin (same as FakePlugin).
e.g. create database "quantum_nec" and user "quantum" at MySQL:

        $ mysql -u root
        mysql> CREATE DATABASE quantum_nec;
        mysql> GRANT ALL PRIVILEGES ON quantum_nec.* TO 'quantum'@'%';
        mysql> GRANT USAGE ON quantum_nec.* to quantum@'%' IDENTIFIED BY 'quantumpass';
        mysql> FLUSH PRIVILEGES;

Disable default Quantum Extentions not supported by the plugin.
NEC extension "vifinfo" must be enabled.

        $ cd quantum-2011.3/extensions
        $ mv credential.py _credential.py
        $ mv multiport.py _multiport.py
        $ mv novatenant.py _novatenant.py
        $ mv portprofile.py _portprofile.py
        $ mv qos.py _qos.py

Edit the plugin configuration file
"quantum-2011.3/quantum/plugins/nec/conf/nec_plugin.ini".
Make sure it matches your database configuration and OFC configuration.
See comments in the plugin configuration file for more information.
An example of configuration:

        [DATABASE]
        name = quantum_nec
        user = quantum
        pass = quantumpass
        host = 127.0.0.1

        [OFC]
        host = 127.0.0.1
        port = 8888

        [AutoID]
        tenant = false
        network = true
        port = false

(Option) You can register default VIF - OpenFlow port mappings.
This option is useful if you had a static OpenFlow port for a gateway
or a tester.
To enable this option, add VIF section and specify filename,
in which VIF - OpenFlow port mappings are listed:

        [VIF]
        filename = quantum/plugins/nec/conf/ofvif.conf

In that file, write down mappings as the following:

        [OFVIF1]
        interface_id = vif01
        datapath_id = 0x12345
        port_no = 1

### OpenStack Nova

For Nova Network, make sure to set up Nova using the QuantumManager
in the nova.conf.  And also set Quantum host.
e.g.:

        --network_manager=nova.network.quantum.manager.QuantumManager
        --quantum_host=192.168.0.1

For Nova Compute, configure the bridge and VIF driver in nova.conf.

        --libvirt_ovs_integration_bridge=br-int
        --libvirt_vif_driver=nova.virt.libvirt.nec.nec_vif_driver.NECVIFDriver
        --libvirt_vif_type=ethernet

At Nova Compute node(s), allow nova_sudoers to run ovs command.
Check /usr/sbin/ovs-vsctl listed in /etc/sudoers.d/nova_sudoers .

Restart Nova services to apply your configuration.

        $ sudo restart nova-compute
        $ sudo restart nova-network
        $ sudo restart nova-scheduler
        $ sudo restart nova-api

### OpenFlow Controller (Trema)

Create configuration database for Sliceable Routing Switch.

        $ cd apps/sliceable_routing_switch
        $ ./create_tables.sh

Fix the database file path in a cgi script
"apps/sliceable_routing_switch/config.cgi" .

        $ sed -i -e "s|/home/sliceable_routing_switch|`pwd`|" config.cgi

Change owner of files that RES API uses.

        $ sudo chown -R www-data.www-data config.cgi Filter.pm  Slice.pm filter.db  slice.db

Configure Apache2 Server for Sliceable Routing Switch.
Copy a sample configuration file into "/etc/apache2/sites-available".
And fix file path and other configurations as you like.

        $ sudo cp apache/sliceable_routing_switch /etc/apache2/sites-available
        $ sudo vi /etc/apache2/sites-available/sliceable_routing_switch

Configure Apache2 to ignore tenants.
This plugin accesses the OFC REST API with tenant name
like "http://tremahost/tenants/hoge/networks".
However, Sliceable Routing Switch REST API does NOT handle tenants.
To solve this difference, add the following RewriteRule
to Apache2 configuration to ignore "tenants/hoge/":

        RewriteRule ^/tenants/[^/]*/networks(.*)$  /networks$1? [QSA,PT]

Reload Apache2 to enable your configuration.

        $ sudo a2enmod rewrite actions
        $ sudo a2ensite sliceable_routing_switch
        $ sudo /etc/init.d/apache2 reload

You can use a Trema configuration file in Sliceable Routing Switch
("apps/sliceable_routing_switch/sliceable_routing_switch_null.conf").
Before you run trema with this config file,
check each path set to properly match TREMA_HOME.

### OpenFlow Switch (Open vSwitch)

Create a bridge for OpenFlow Network, and connect to the OFC.
e.g. create bridge "br-int" and set OFC IP address:

        # ovs-vsctl add-br br-int
        # ovs-vsctl set-controller br-int tcp:192.168.0.2

To link another OFS with an exclusive link, set interface and plug it.
e.g. use eth1 to link bridge "br-int" to the next OpenFlow switch:

        # ifconfig eth1 0.0.0.0 up
        # ip link set eth1 promisc on
        # ovs-vsctl add-port br-int eth1

To link another OFS with a GRE tunnel,
configure GRE type interface on both side of the link.
e.g. config a GRE tunnel between Host A (192.168.100.3)
and Host B (192.168.100.4) as follows:

        (At Host A)
        # ovs-vsctl add-port br-int gre0 -- set Interface gre0 type=gre options:remote_ip=192.168.100.4
        (At Host B)
        # ovs-vsctl add-port br-int gre0 -- set Interface gre0 type=gre options:remote_ip=192.168.100.3


Start Services
--------------

Commands to start services are depends on your installations and
configurations.  If you has installed Nova and Open vSwitch with deb packages,
probably Nova and Open vSwitch has started already.
Start Trema and Quantum as follows:

        $ cd trema
        $ sudo ./trema run -d -c ../apps/sliceable_routing_switch/sliceable_routing_switch_null.conf
        $ cd ../quantum-2011.3/
        $ PYTHONPATH=".:$PYTHONPATH" python bin/quantum etc/quantum.conf

Then, you can use the following commands
(For details see each command's help message or document):

* /usr/bin/nova-manage
* /usr/bin/nova
* quantum/bin/cli
* apps/sliceable_routing_switch/slice
* apps/sliceable_routing_switch/filter


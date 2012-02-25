Quick Start Installer
=====================


What is Quick Start Installer?
------------------------------

Quick Start Installer is a script to build an OpenStack environment with
the Quantum NEC Plugin in one machine.  This installer installs and
configures all services that the Quantum NEC OpenFlow Plugin needs.
You can get a trial environment in ten and several minutes!


Restrictions
------------

* This installer DO NOT support OS installation.
  Install and setup OS by yourself (setup network, sudo, etc.).
* Supported distribution is Ubuntu 11.04.
* This installer installs minimun components of OpneStack to use Quantum;
  Keystone, Dashboard, and Swift are NOT included.
* Use MySQL Database.
* Run this installer as a regular user with sudo privileges.


Target Softwares
----------------

* Nova (deb packages, current version 2011.3)
* Quantum (version 2011.3) with the NEC Plugin
* Trema and Trema App - Sliceable Routing Switch
* Open vSwitch (deb package)


Configurations
--------------

Configure `quickstart/installerrc'.  Set the following parameters:

* HOST_IP: (Option) IP Address of the target HOST
  (If HOST_IP is not specified, the installer use eth0's IP address.)
* MYSQL_PASS: MySQL root password
* NDB_PASS: Nova Database password for user "nova"
* QDB_NAME: Quantum Database name
* QDB_USER: Quantum Database username
* QDB_PASS: Quantum Database password for $QDB_USER
* BRIDGE: Bridge name on Open vSwitch
* USER: (Option) Nova test USER
* PROJECT: (Option) Nova test PROJECT
  (If USER and PROJECT are specified, the installer creates project on Nova.)
* IMAGE_TAR, IMAGE_URL: (Option) Public Image to register
  (IMAGE format must be in a form acceptable to `nova-manage image convert'.
  The installer checsk a TAR file first.  If the TAR file is not exist,
  the installer downloads IMAGE from specified URL.
  Then the installer registers this IMAGE to Nova as a Public VM image.)


Run Installer
-------------

Run `installer.sh', and wait...

        $ ./installer.sh

After installation has finished, check console output and log files.
The log files can be found at:

* Nova:    /var/log/nova/
* Quantum: quantum-nec-of-plugin/quantum/quantum-server.log
* Trema:   quantum-nec-of-plugin/quickstart/trema/trema/tmp/log/

If you has configured USER and PROJECT,
you can find the following items are created:

* script "quickstart/create-private-network.sh"
  (This script create two networks and plug veth interfaces into each network.)
* credentials under quickstart/creds/

If you has configured IMAGE_*,
you can see the registered IMAGE by command `euca-describe-images'.


Test VM Launch
--------------

1. Load novarc.

        $ source quickstart/creds/novarc

2. Check IP address range in the script, and run it.
   Set parameter: `(<Label> <IP Address/cidr> <Size of the network> <Gateway>)`.

        $ ./create-private-network.sh

3. Launch VM.
   e.g.:

        $ euca-run-instances -k usagi -t m1.tiny ami-00000003
        or
        $ nova boot --image 3 --flavor 1 --meta key=usagi servera

4. Check Status

        $ euca-describe-instances
        or
        $ nova list

5. Ping, SSH, etc...  Enjoy!

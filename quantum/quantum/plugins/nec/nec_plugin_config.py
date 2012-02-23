# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import ConfigParser
import logging
from optparse import OptionParser
import os
import sys

LOG = logging.getLogger('nec_plugin_config')
CONF_FILE = "conf/nec_plugin.ini"


class NECConfig(object):

    def __init__(self, config_file=None):
        config = ConfigParser.ConfigParser()
        if not config_file:
            dir = os.path.dirname(os.path.realpath(__file__))
            config_file = dir + "/" + CONF_FILE
        if not os.path.exists(config_file):
            raise Exception("Configuration file \"%s\" doesn't exist." %
              (config_file))
        LOG.debug("Using configuration file \"%s\"" % config_file)

        config.read(config_file)
        LOG.debug("Config: %s" % config)

        if config.has_option("DATABASE", "sql_connection"):
            self.DB = config.get("DATABASE", "sql_connection")
        else:
            db_name = config.get("DATABASE", "name")
            db_user = config.get("DATABASE", "user")
            db_pass = config.get("DATABASE", "pass")
            db_host = config.get("DATABASE", "host")
            self.DB = "mysql://%s:%s@%s/%s" % \
                        (db_user, db_pass, db_host, db_name)

        self.OFC_HOST = config.get("OFC", "host")
        self.OFC_PORT = config.get("OFC", "port")

        self.vif_file = None
        if config.has_section("VIF") and config.has_option("VIF", "filename"):
            filename = config.get("VIF", "filename")
            if os.path.exists(filename):
                self.vif_file = filename
            else:
                dir = os.path.dirname(os.path.realpath(__file__))
                fullpath = dir + "/" + filename
                if os.path.exists(fullpath):
                    self.vif_file = filename
                else:
                    LOG.warning("Ignore VIF conf file: %s" % filename)

        self.auto_id_tenant = config.getboolean("AutoID", "tenant")
        self.auto_id_network = config.getboolean("AutoID", "network")
        self.auto_id_port = config.getboolean("AutoID", "port")
        LOG.debug("AutoID tenant: %s, network:%s, port:%s" %
                  (self.auto_id_tenant,
                   self.auto_id_network,
                   self.auto_id_port))

    def load_vifinfo(self, filename):
        config = ConfigParser.ConfigParser()
        config.read(filename)
        vifinfo_list = []
        for section in config.sections():
            LOG.debug("Parse section=[%s]" % section)
            items = config.items(section)
            vifinfo = {}
            vifinfo['vlan_id'] = 65535
            for item in items:
                if item[0] == "interface_id":
                    vifinfo['interface_id'] = item[1]
                elif item[0] == "datapath_id":
                    vifinfo['datapath_id'] = item[1]
                elif item[0] == "port_no":
                    vifinfo['port_no'] = int(item[1])
                elif item[0] == "vlan_id":
                    vifinfo['vlan_id'] = int(item[1])
                else:
                    LOG.warning("Ignore key_name[%s]." % item[0])

            LOG.debug("interface_id = %s, datapath_id = %s, "
                      "port_no = %s, vlan_id = %d." %
                      (vifinfo['interface_id'],
                       vifinfo['datapath_id'],
                       vifinfo['port_no'],
                       vifinfo['vlan_id']))
            if vifinfo['vifid'] and vifinfo['dpid'] and vifinfo['port_no']:
                vifinfo_list.append(vifinfo)
            else:
                LOG.warning("Ignore section=[%s]" % section)
        return vifinfo_list

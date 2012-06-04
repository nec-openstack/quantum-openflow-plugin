# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import ConfigParser
import logging
from optparse import OptionParser
import os

from quantum.common.config import find_config_file
from quantum.plugins.nec.drivers.trema_port import TremaPortBaseDriver
from quantum.plugins.nec.drivers.trema_portmac import TremaPortMACBaseDriver
from quantum.plugins.nec.drivers.trema_mac import TremaMACBaseDriver
from quantum.plugins.nec.drivers.pfc import PFCDriver

LOG = logging.getLogger(__name__)
CONF_FILE = find_config_file({'plugin': 'nec'}, None, "nec.ini")
driver_list = {'trema_port': TremaPortBaseDriver,
               'trema_portmac': TremaPortMACBaseDriver,
               'trema_mac': TremaMACBaseDriver,
               'pfc': PFCDriver}


class NECConfig(object):

    def __init__(self, config_file=None):
        config = ConfigParser.ConfigParser()
        if config_file is None:
            config_file = CONF_FILE
        if not os.path.exists(config_file):
            raise Exception("Configuration file \"%s\" doesn't exist." %
                            (config_file))
        LOG.debug("Using configuration file: %s" % config_file)
        config.read(config_file)
        LOG.debug("Config file: %s" % config)

        if config.has_option("DATABASE", "sql_connection"):
            self.DB = config.get("DATABASE", "sql_connection")
        else:
            db_name = config.get("DATABASE", "name")
            db_user = config.get("DATABASE", "user")
            db_pass = config.get("DATABASE", "pass")
            db_host = config.get("DATABASE", "host")
            self.DB = "mysql://%s:%s@%s/%s" % \
                        (db_user, db_pass, db_host, db_name)
        LOG.debug("DB: %s" % self.DB)

        self.OFC_HOST = config.get("OFC", "host")
        self.OFC_PORT = config.get("OFC", "port")
        driver_str = config.get("OFC", "driver")
        self.OFC_DRIVER = driver_list.get(driver_str, None)
        if not self.OFC_DRIVER:
            raise Exception("Not found driver \"%s\"." % driver_str)
        LOG.debug("OFC: %s:%s (driver=%s)." %
                  (self.OFC_HOST, self.OFC_PORT, driver_str))

        filter_enabled = config.getboolean("OFC", "enable_filter")
        if filter_enabled and not self.OFC_DRIVER.filter_supported():
            LOG.warning("driver [%s] does NOT support filter." % driver_str)
            filter_enabled = False
        self.FILTER = filter_enabled
        LOG.debug("OFC: filter_enabled=%s." % self.FILTER)

#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.

import gettext
import logging
import logging.handlers
import os
import json
import sys

from optparse import OptionParser

from vifinfo_client import VIFINFOClient

LOG = logging.getLogger('vifinfo_cli')


def help():
    print "\nCommands:"
    commands = {
      "list_vifinfos": {
        "args": []},
      "create_vifinfo": {
        "args": ["vif-id", "datapath-id", "port-no"]},
      "show_vifinfo": {
        "args": ["vif-id"]},
      "delete_vifinfo": {
        "args": ["vif-id"]},
      "update_vifinfo": {
        "args": ["vif-id", "datapath-id", "port-no"]}}
    for k in commands.keys():
        print "    %s %s" % (k,
          " ".join(["<%s>" % y for y in commands[k]['args']]))


def build_args(cmd, cmdargs, arglist):
    args = []
    orig_arglist = arglist[:]
    try:
        for x in cmdargs:
            args.append(arglist[0])
            del arglist[0]
    except:
        LOG.error("Not enough arguments for \"%s\" (expected: %d, got: %d)" %
                  (cmd, len(cmdargs), len(orig_arglist)))
        print "Usage:\n    %s %s" % (cmd,
          " ".join(["<%s>" % y for y in commands[cmd]['args']]))
        return None
    if len(arglist) > 0:
        LOG.error("Too many arguments for \"%s\" (expected: %d, got: %d)" %
                  (cmd, len(cmdargs), len(orig_arglist)))
        print "Usage:\n    %s %s" % (cmd,
          " ".join(["<%s>" % y for y in commands[cmd]['args']]))
        return None
    return args


def print_ret(data):
    if "vifinfos" in data:
        for vifinfo in data['vifinfos']:
            print "Interface ID: %s" % vifinfo['interface_id']
    if "vifinfo" in data:
        vifinfo = data['vifinfo']
        print "Interface ID: %s" % vifinfo['interface_id']
        if "ofs_port" in vifinfo:
            ofs_port = vifinfo['ofs_port']
            print "        Datapath ID: %s" % ofs_port['datapath_id']
            print "        OFPort No:   %s" % ofs_port['port_no']


if __name__ == "__main__":
    usagestr = "Usage: %prog [OPTIONS] <command> [args]"
    parser = OptionParser(usage=usagestr)
    parser.add_option("-H", "--host", dest="host",
      type="string", default="127.0.0.1", help="ip address of api host")
    parser.add_option("-p", "--port", dest="port",
      type="int", default=9696, help="api poort")
    parser.add_option("-v", "--verbose", dest="verbose",
      action="store_true", default=False, help="turn on verbose logging")
    parser.add_option("-f", "--logfile", dest="logfile",
      type="string", default="syslog", help="log file path")
    options, args = parser.parse_args()

    if options.verbose:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.WARN)
    #logging.handlers.WatchedFileHandler

    if options.logfile == "syslog":
        LOG.addHandler(logging.handlers.SysLogHandler(address='/dev/log'))
    else:
        LOG.addHandler(logging.handlers.WatchedFileHandler(options.logfile))
        # Set permissions on log file
        os.chmod(options.logfile, 0644)

    if len(args) < 1:
        parser.print_help()
        help()
        sys.exit(1)

    client = VIFINFOClient(options.host, options.port, cli=True)
    commands = {
      "list_vifinfos": {
        "func": client.list_vifinfos,
        "args": []},
      "create_vifinfo": {
        "func": client.create_vifinfo,
        "args": ["vif-id", "datapath-id", "port-no"]},
      "show_vifinfo": {
        "func": client.show_vifinfo,
        "args": ["vif-id"]},
      "delete_vifinfo": {
        "func": client.delete_vifinfo,
        "args": ["vif-id"]},
      "update_vifinfo": {
        "func": client.update_vifinfo,
        "args": ["vif-id", "datapath-id", "port-no"]}}

    cmd = args[0]
    if cmd not in commands.keys():
        LOG.error("Unknown command: %s" % cmd)
        help()
        sys.exit(1)

    args = build_args(cmd, commands[cmd]['args'], args[1:])
    LOG.info("Executing command \"%s\" with args: %s" % (cmd, args))

    ret = commands[cmd]['func'](*args)
    if ret:
        print_ret(ret)

    LOG.info("Command execution completed")
    sys.exit(0)

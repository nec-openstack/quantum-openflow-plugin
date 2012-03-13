# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import re
import uuid
from webob import exc

import netaddr

from quantum.api import api_common as common
from quantum.api import networks
from quantum.common import exceptions as qexception
from quantum.common import extensions
from quantum.manager import QuantumManager


class Filter(object):

    def __init__(self):
        pass

    def get_name(self):
        return "filters"

    def get_alias(self):
        return "FILTERS"

    def get_description(self):
        return "The Filters on OpenFlow Controller API Extension."

    def get_namespace(self):
        return "http://www.nec.co.jp/api/ext/filter/v1.0"

    def get_updated(self):
        return "2011-01-22T21:53:00+09:00"

    def get_resources(self):
        parent_resource = dict(member_name="network",
                               collection_name="/tenants/{tenant_id}/networks")
        controller = FilterController(QuantumManager.get_plugin())
        return [extensions.ResourceExtension('filters', controller,
                                             parent=parent_resource)]


class FilterController(common.QuantumController):
    """
    Ofport API controller maps/unmaps Interfaces to OpenFlow Ports.
    """

    def __init__(self, plugin):
        self.plugin = plugin

    def _parse_request_params(self, request):
        """
        An Acceptable Filter Request format is:
.
        {"filter":
            {"action": "<Action (ACCEPT/DROP)>",
             "priority": "<Priority Number (1-32766)>",
             "condition":
                 {"in_port": "<Port ID on the Quantum Server>",
                  "src_mac": "<Source MAC Address>",
                  "dst_mac": "<Destination MAC Address>",
                  "src_cidr": "<Source IP Address>",
                  "dst_cidr": "<Destination IP Address>",
                  "protocol": "<Protocol Name (ARP/ICMP/TCP/UDP)>",
                  "src_port": "<Source L4 Port Number>",
                  "dst_port": "<Destination L4 Port Number>"}}}

        Note: each param in condition is optional.
        """
        if not request.body:
            raise exc.HTTPBadRequest("No body.")
        data = self._deserialize(request.body,
                                 request.best_match_content_type())
        params = {}
        filter = data.get('filter', None)
        if not filter:
            raise exc.HTTPBadRequest("No filter.")

        action = filter.get('action', None)
        if not action:
            raise exc.HTTPBadRequest("No action.")
        if action.upper() not in ("ACCEPT", "DROP"):
            raise exc.HTTPBadRequest("Bad action %s." % action)
        params['action'] = action.upper()

        priority = filter.get('priority', None)
        if not priority:
            raise exc.HTTPBadRequest("No priority.")
        p = int(priority)
        if p < 1 or 32766 < p:
            raise exc.HTTPBadRequest("Bad priority %s." % priority)
        params['priority'] = p

        condition = filter.get('condition', None)
        params['condition'] = {}
        if not condition:
            return params

        def _validate_in_port(in_port):
            if in_port:
                try:
                    uuid.UUID(in_port)
                except (TypeError, ValueError, AttributeError):
                    raise exc.HTTPBadRequest("Bad in_port %s." % in_port)

        params['condition']['in_port'] = condition.get('in_port', None)
        _validate_in_port(params['condition']['in_port'])

        def _validate_mac(mac, param):
            if mac:
                macl = mac.lower()
                if not re.match("[0-9a-f]{2}([-:][0-9a-f]{2}){5}$", macl):
                    raise exc.HTTPBadRequest("Bad %s %s." % (param, mac))

        params['condition']['src_mac'] = condition.get('src_mac', None)
        _validate_mac(params['condition']['src_mac'], "src_mac")
        params['condition']['dst_mac'] = condition.get('dst_mac', None)
        _validate_mac(params['condition']['dst_mac'], "dst_mac")

        def _validate_cidr(cidr, param):
            if cidr:
                try:
                    netaddr.IPNetwork(cidr)
                except ValueError:
                    raise exc.HTTPBadRequest("Bad %s %s." % (param, cidr))

        params['condition']['src_cidr'] = condition.get('src_cidr', None)
        _validate_cidr(params['condition']['src_cidr'], "src_cidr")
        params['condition']['dst_cidr'] = condition.get('dst_cidr', None)
        _validate_cidr(params['condition']['dst_cidr'], "dst_cidr")

        def _parse_protocol(protocol):
            if not protocol:
                return None
            if protocol.upper() not in ("ARP", "ICMP", "TCP", "UDP"):
                raise exc.HTTPBadRequest("Bad protocol %s." % protocol)
            return protocol.upper()

        params['condition']['protocol'] = \
          _parse_protocol(condition.get('protocol', None))

        def _parse_l4_port(l4_port, param):
            if not l4_port:
                return None
            try:
                return int(l4_port)
            except Exception:
                raise exc.HTTPBadRequest("Bad %s %s." % (param, l4_port))

        params['condition']['src_port'] = \
          _parse_l4_port(condition.get('src_port', None), "src_port")
        params['condition']['dst_port'] = \
          _parse_l4_port(condition.get('dst_port', None), "dst_port")

        return params

    def index(self, request, tenant_id, network_id):
        return self.plugin.list_filters(tenant_id, network_id)

    def show(self, request, tenant_id, network_id, id):
        return self.plugin.get_filter(tenant_id, network_id, id)

    def create(self, request, tenant_id, network_id):
        filter_dict = self._parse_request_params(request)
        return self.plugin.add_filter(tenant_id, network_id, filter_dict)

    def update(self, request, tenant_id, network_id, id):
        filter_dict = self._parse_request_params(request)
        self.plugin.update_filter(tenant_id, network_id, id, filter_dict)
        return exc.HTTPNoContent()

    def delete(self, request, tenant_id, network_id, id):
        self.plugin.delete_filter(tenant_id, network_id, id)
        return exc.HTTPNoContent()

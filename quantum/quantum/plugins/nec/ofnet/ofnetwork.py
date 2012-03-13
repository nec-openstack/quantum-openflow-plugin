# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import httplib
import json
import logging
from webob import exc

from quantum.common.wsgi import Serializer

# Action query strings for ofnetwork
tenants_path = "/tenants"
tenant_path = "/tenants/%s"
networks_path = "/tenants/%s/networks"
network_path = "/tenants/%s/networks/%s"
ports_path = "/tenants/%s/networks/%s/ports"
port_path = "/tenants/%s/networks/%s/ports/%s"
filters_path = "/tenants/%s/filters"
filter_path = "/tenants/%s/filters/%s"

LOG = logging.getLogger('nec_plugin.ofnetwork')


class OFNetwork():

    def __init__(self, host='localhost', port=8888):
        self.ofn_server = "%s:%s" % (host, port)
        self.format = "json"

    def request(self, method, path, body=None, json_dumps=False):
        LOG.debug("request() called: %s %s %s" % (method, path, body))
        if body:
            if json_dumps:
                body = json.dumps(body)
            else:
                body = self.serialize(body)

        conn = httplib.HTTPConnection(self.ofn_server)
        if method == "POST" or "PUT":
            header = {'Content-Type': "application/json"}
            conn.request(method, path, body, header)
        else:
            conn.request(method, path, body)
        res = conn.getresponse()
        conn.close
        LOG.debug("request(): OFC returns %s(%s)" % (res.status, res.reason))
        status_code = self.get_status_code(res)
        data = res.read()
        if method in ("GET"):
            if res.status != httplib.OK:
                """200"""
                LOG.warning("request(): bad response `%s' for method `%s'" %
                            (res.status, method))
        elif method in ("POST", "DELETE", "PUT"):
            if res.status != httplib.ACCEPTED:
                """202"""
                LOG.warning("request(): bad response `%s' for method `%s'" %
                            (res.status, method))
        LOG.debug("request(): OFC returns data = %s" % (data))

        if status_code in (httplib.OK, httplib.ACCEPTED):
            return self.deserialize(data, status_code)
        else:
            error_message = data
            LOG.debug("request(): Server returned error: %s" % status_code)
            LOG.debug("request(): Error message: %s" % error_message)
            # error_message = {res.reason:
            #                     {'message': error_message,
            #                      'code': status_code,
            #                      'detail': error_message}}
            if status_code == httplib.NOT_FOUND:
                """404"""
                raise exc.HTTPNotFound(error_message)
            elif status_code == httplib.METHOD_NOT_ALLOWED:
                """405"""
                raise exc.HTTPMethodNotAllowed(error_message)
            elif status_code == httplib.UNPROCESSABLE_ENTITY:
                """422"""
                raise exc.HTTPUnprocessableEntity(error_message)
            elif status_code == httplib.NOT_IMPLEMENTED:
                """501"""
                raise exc.HTTPNotImplemented(error_message)
            else:
                """other error is 500"""
                raise exc.HTTPInternalServerError(error_message)

    def get_status_code(self, response):
        """
        Returns the integer status code from the response, which
        can be either a Webob.Response (used in testing) or httplib.Response
        """
        if hasattr(response, 'status_int'):
            return response.status_int
        else:
            return response.status

    def serialize(self, data):
        """
        Serializes a dictionary with a single key (which can contain any
        structure) into either xml or json
        """
        if data is None:
            return None
        elif type(data) is dict:
            return Serializer().serialize(data, self.content_type())
        else:
            raise Exception("unable to deserialize object of type = '%s'" \
                                % type(data))

    def deserialize(self, data, status_code):
        """
        Deserializes a an json string into a dictionary
        """
        LOG.debug("deserialize called. data='%s'" % data)
        if status_code == httplib.NO_CONTENT or len(data) is 0:
            return data
        return Serializer().deserialize(data, self.content_type())

    def content_type(self, format=None):
        """
        Returns the mime-type for either 'xml' or 'json'.  Defaults to the
        currently set format
        """
        if not format:
            format = self.format
        return "application/%s" % (format)

    def ofn_create_tenant(self, description, ofn_tenant_id=None):
        """
        Create a new tenant.
        'id' is automatically assigned if ofn_tenant_id is None..
        """
        LOG.debug("ofn_create_tenant() called: description = %s, "
                  "ofn_tenant_id = %s." % (description, ofn_tenant_id))
        path = tenants_path
        if ofn_tenant_id:
            body = {'id': ofn_tenant_id, 'description': description}
        else:
            body = {'description': description}

        res = self.request("POST", path, body)
        return res

    def ofn_delete_tenant(self, ofn_tenant_id):
        """
        Remove the tenant identified by ofn_tenant_id.
        """
        LOG.debug("ofn_delete_tenant() called: ofn_tenant_id = %s." %
                  ofn_tenant_id)
        path = tenant_path % ofn_tenant_id
        res = self.request("DELETE", path, None)

    def ofn_create_network(self, ofn_tenant_id, description,
                           ofn_network_id=None):
        """
        Create a new network associated with a tenant.
        'id' is automatically assigned if ofn_network_id is None .
        """
        LOG.debug("ofn_create_network() called: ofn_tenant_id = %s, "
                  "description = %s, ofn_network_id = %s." %
                  (ofn_tenant_id, description, ofn_network_id))
        path = networks_path % ofn_tenant_id
        if ofn_network_id:
            body = {'id': ofn_network_id, 'description': description}
        else:
            body = {'description': description}

        res = self.request("POST", path, body)
        return res

    def ofn_rename_network(self, ofn_tenant_id, ofn_network_id, description):
        """
        Rename the network identified by ofn_network_id.
        """
        LOG.debug("ofn_rename_network() called: ofn_tenant_id = %s, "
                  "ofn_network_id = %s, description = %s." %
                  (ofn_tenant_id, ofn_network_id, description))
        path = network_path % (ofn_tenant_id, ofn_network_id)
        body = {'description': description}
        res = self.request("PUT", path, body)
        return res

    def ofn_delete_network(self, ofn_tenant_id, ofn_network_id):
        """
        Remove the network identified by ofn_network_id.
        """
        LOG.debug("ofn_delete_network() called: ofn_tenant_id = %s, "
                  "ofn_network_id = %s." % (ofn_tenant_id, ofn_network_id))
        path = network_path % (ofn_tenant_id, ofn_network_id)
        res = self.request("DELETE", path)

    def ofn_create_port(self, ofn_tenant_id, ofn_network_id,
                        datapath_id, port_no, vlan_id=65535, ofn_port_id=None):
        """
        Create a port on the network specified by ofn_network_id.
        'id' is automatically assigned if ofn_port_id is None .
        """
        LOG.debug("ofn_create_port() called: ofn_tenant_id = %s, "
                  "ofn_network_id = %s, datapath_id = %s, port_no = %s, "
                  "vlan_id = %s, ofn_port_id = %s." %
                  (ofn_tenant_id, ofn_network_id, datapath_id, port_no,
                   vlan_id, ofn_port_id))
        path = ports_path % (ofn_tenant_id, ofn_network_id)
        if ofn_port_id:
            body = {'id': ofn_port_id,
                    'datapath_id': datapath_id,
                    'port': port_no,
                    'vid': vlan_id}
        else:
            body = {'datapath_id': datapath_id,
                    'port': port_no,
                    'vid': vlan_id}

        res = self.request("POST", path, body)
        return res

    def ofn_delete_port(self, ofn_tenant_id, ofn_network_id, ofn_port_id):
        """
        Remove a port from the network.
        """
        LOG.debug("ofn_delete_port() called: ofn_tenant_id = %s, "
                  "ofn_network_id = %s, ofn_port_id = %s." %
                  (ofn_tenant_id, ofn_network_id, ofn_port_id))
        path = port_path % (ofn_tenant_id, ofn_network_id, ofn_port_id)
        res = self.request("DELETE", path)

    def ofn_create_filter(self, ofn_tenant_id, ofn_network_id,
                          filter, vifinfo=None, ofn_filter_id=None):
        """
        Create a filter.
        """
        LOG.debug("ofn_create_filter() called: ofn_tenant_id = %s, "
                  "ofn_network_id = %s, filter = %s, vifinfo = %s, "
                  "ofn_filter_id = %s" %
                  (ofn_tenant_id, ofn_network_id,
                   filter, vifinfo, ofn_filter_id))
        path = filters_path % ofn_tenant_id

        if filter.action.upper() in "ACCEPT":
            ofn_action = "ALLOW"
        elif filter.action.upper() in "DROP":
            ofn_action = "DENY"

        body = {'priority': filter.priority,
                'slice': ofn_network_id,
                'action': ofn_action}
        ofp_wildcards = ["dl_vlan", "dl_vlan_pcp", "nw_tos"]

        if vifinfo:
            body['in_datapath_id'] = vifinfo.datapath_id
            body['in_port'] = vifinfo.port_no
        else:
            body['wildcards'] = "in_datapath_id"
            ofp_wildcards.append("in_port")

        if filter.src_mac:
            body['dl_src'] = filter.src_mac
        else:
            ofp_wildcards.append("dl_src")

        if filter.dst_mac:
            body['dl_dst'] = filter.dst_mac
        else:
            ofp_wildcards.append("dl_dst")

        if filter.src_cidr:
            body['nw_src'] = filter.src_cidr
        else:
            ofp_wildcards.append("nw_src:32")

        if filter.dst_cidr:
            body['nw_dst'] = filter.dst_cidr
        else:
            ofp_wildcards.append("nw_dst:32")

        if filter.protocol:
            if filter.protocol.upper() in "ICMP":
                body['dl_type'] = "0x800"
                body['nw_proto'] = hex(1)
            elif filter.protocol.upper() in "TCP":
                body['dl_type'] = "0x800"
                body['nw_proto'] = hex(6)
            elif filter.protocol.upper() in "UDP":
                body['dl_type'] = "0x800"
                body['nw_proto'] = hex(17)
            elif filter.protocol.upper() in "ARP":
                body['dl_type'] = "0x806"
                ofp_wildcards.append("nw_proto")
            else:
                msg = "unknown protocol %s." % filter.protocol
                LOG.error("ofn_create_filter(): %s" % msg)
                raise exc.HTTPInternalServerError(msg)
        else:
            ofp_wildcards.append("dl_type")
            ofp_wildcards.append("nw_proto")

        if filter.src_port:
            body['tp_src'] = hex(filter.src_port)
        else:
            ofp_wildcards.append("tp_src")

        if filter.dst_port:
            body['tp_dst'] = hex(filter.dst_port)
        else:
            ofp_wildcards.append("tp_dst")

        if ofn_filter_id:
            body['id'] = ofn_filter_id

        body['ofp_wildcards'] = ','.join(ofp_wildcards)
        res = self.request("POST", path, [body], True)
        return res

    def ofn_delete_filter(self, ofn_tenant_id, ofn_filter_id):
        """
        Remove a filter.
        """
        LOG.debug("ofn_delete_filter() called: ofn_tenant_id = %s, "
                  "ofn_filter_id = %s" % (ofn_tenant_id, ofn_filter_id))
        path = filter_path % (ofn_tenant_id, ofn_filter_id)
        res = self.request("DELETE", path)

# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import httplib
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

LOG = logging.getLogger('nec_plugin.ofnetwork')


class OFNetwork(object):

    def __init__(self, host='localhost', port=8888):
        self.ofn_server = "%s:%s" % (host, port)
        self.format = "json"

    def request(self, method, path, body=None):
        LOG.debug("request() called: %s %s %s" % (method, path, body))
        if body:
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
        if method in ("GET", "POST"):
            if res.status != 200:
                LOG.warning("request(): bad response `%s' for method `%s'" %
                            (res.status, method))
        elif method in ("DELETE", "PUT"):
            if res.status != 204:
                LOG.warning("request(): bad response `%s' for method `%s'" %
                            (res.status, method))
        LOG.debug("request(): OFC returns data = %s" % (data))

        if status_code in (httplib.OK,
                           httplib.CREATED,
                           httplib.ACCEPTED,
                           httplib.NO_CONTENT):
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

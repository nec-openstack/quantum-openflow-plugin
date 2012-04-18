# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import httplib
import json
from webob import exc


class VIFINFOClient(object):

    def __init__(self, host, port, cli=False):
        if cli:
            import logging
            self.LOG = logging.getLogger("vifinfo_client")
        else:
            from nova import log as logging
            self.LOG = \
              logging.getLogger("nova.virt.libvirt.nec.vifinfo_client")
        self.server = "%s:%s" % (host, port)
        self.LOG.debug("quantum server: %s" % self.server)

    def vifinfo_request(self, method, path, body=None):
        self.LOG.debug("vifinfo_request() called:%s %s %s" %
                       (method, path, body))
        if body:
            body = json.dumps(body)
        conn = httplib.HTTPConnection(self.server)
        if method == "POST" or "PUT":
            header = {'Content-Type': "application/json"}
            conn.request(method, path, body, header)
        else:
            conn.request(method, path, body)
        res = conn.getresponse()
        conn.close
        self.LOG.debug("vifinfo_request(): Quantum server returns %s(%s)" %
                  (res.status, res.reason))
        if hasattr(res, 'status_int'):
            status_code = res.status_int
        else:
            status_code = res.status
        data = res.read()
        if method in ("GET", "POST"):
            if res.status != 200:
                self.LOG.warning("vifinfo_request(): bad response `%s' "
                                 "for method `%s'" % (res.status, method))
        elif method in ("DELETE", "PUT"):
            if res.status != 204:
                self.LOG.warning("vifinfo_request(): bad response `%s' "
                                 "for method `%s'" % (res.status, method))

        if status_code in (httplib.OK,
                           httplib.CREATED,
                           httplib.ACCEPTED):
            return json.loads(data)
        elif status_code == httplib.NO_CONTENT:
            return None
        else:
            error_message = data
            self.LOG.debug("Server returned error: %s" % status_code)
            self.LOG.debug("Error message: %s" % error_message)
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

    def list_vifinfos(self):
        self.LOG.debug("list_vifinfo() called")
        return self.vifinfo_request("GET", "/v1.0/vifinfos")

    def create_vifinfo(self, interface_id, datapath_id, port_no):
        self.LOG.debug("create_vifinfo() called: interface_id = %s, "
                       "datapath_id = %s, port_no = %s." %
                       (interface_id, datapath_id, port_no))
        body = {'vifinfo': {'interface_id': interface_id,
                            'ofs_port': {'datapath_id': datapath_id,
                                         'port_no': port_no}}}
        return self.vifinfo_request("POST", "/v1.0/vifinfos", body)

    def show_vifinfo(self, interface_id):
        self.LOG.debug("show_vifinfo() called: interface_id = %s." %
                       (interface_id))
        path = "/v1.0/vifinfos/%s" % interface_id
        try:
            return self.vifinfo_request("GET", path)
        except exc.HTTPNotFound:
            return None

    def delete_vifinfo(self, interface_id):
        self.LOG.debug("delete_vifinfo() called: interface_id = %s." %
                       (interface_id))
        path = "/v1.0/vifinfos/%s" % interface_id
        self.vifinfo_request("DELETE", path)

    def update_vifinfo(self, interface_id, datapath_id, port_no):
        self.LOG.debug("update_vifinfo() called: interface_id = %s, "
                       "datapath_id = %s, port_no = %s." %
                       (interface_id, datapath_id, port_no))
        body = {'vifinfo': {'interface_id': interface_id,
                            'ofs_port': {'datapath_id': datapath_id,
                                         'port_no': port_no}}}
        path = "/v1.0/vifinfos/%s" % interface_id
        return self.vifinfo_request("PUT", path, body)

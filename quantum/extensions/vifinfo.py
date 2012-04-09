# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

from webob import exc

from quantum.api import api_common as common
from quantum.common import exceptions as qexception
from quantum.common import extensions
from quantum.manager import QuantumManager


class Vifinfo(object):

    def __init__(self):
        pass

    def get_name(self):
        return "vifinfos"

    def get_alias(self):
        return "VIFINFOS"

    def get_description(self):
        return "The Virtual Interface - OpenFlow Port Mapping API Extension."

    def get_namespace(self):
        return "http://www.nec.co.jp/api/ext/vifinfo/v1.0"

    def get_updated(self):
        return "2011-01-22T21:53:00+09:00"

    def get_resources(self):
        controller = VifinfoController(QuantumManager.get_plugin())
        return [extensions.ResourceExtension('vifinfos', controller)]


class VifinfoController(common.QuantumController):
    """
    Ofport API controller maps/unmaps Interfaces to OpenFlow Ports.
    """

    def __init__(self, plugin):
        self.plugin = plugin

    def _parse_request_params(self, request):
        if not request.body:
            raise exc.HTTPBadRequest("No body.")
        data = self._deserialize(request.body,
                                 request.best_match_content_type())
        params = {}
        vifinfo = data.get('vifinfo', None)
        if not vifinfo:
            raise exc.HTTPBadRequest("No vifinfo.")
        params['interface_id'] = vifinfo.get('interface_id', None)
        if not params['interface_id']:
            raise exc.HTTPBadRequest("No interface_id.")
        ofs_port = vifinfo.get('ofs_port', None)
        if not ofs_port:
            raise exc.HTTPBadRequest("No ofs_port.")
        params['datapath_id'] = ofs_port.get('datapath_id', None)
        if not params['datapath_id']:
            raise exc.HTTPBadRequest("No datapath_id.")
        port_no = ofs_port.get('port_no', None)
        if not port_no:
            raise exc.HTTPBadRequest("No port_no.")
        params['port_no'] = int(port_no)
        vlan_id = ofs_port.get('vlan_id', None)
        if vlan_id:
            params['vlan_id'] = int(vlan_id)
        else:
            params['vlan_id'] = 65535
        return params

    def index(self, request):
        return self.plugin.list_vifinfos()

    def show(self, request, id):
        vifinfo = self.plugin.get_vifinfo(id)
        if not vifinfo:
            raise exc.HTTPNotFound()
        return vifinfo

    def create(self, request):
        params = self._parse_request_params(request)
        self.plugin.add_vifinfo(params['interface_id'],
                                params['datapath_id'],
                                params['port_no'],
                                params['vlan_id'])
        return {'vifinfo': {'interface_id': params['interface_id']}}

    def update(self, request, id):
        vifinfo = self.plugin.get_vifinfo(id)
        if not vifinfo:
            raise exc.HTTPNotFound()
        params = self._parse_request_params(request)
        self.plugin.delete_vifinfo(id)
        self.plugin.add_vifinfo(params['interface_id'],
                                params['datapath_id'],
                                params['port_no'],
                                params['vlan_id'])
        return exc.HTTPNoContent()

    def delete(self, request, id):
        vifinfo = self.plugin.get_vifinfo(id)
        if not vifinfo:
            raise exc.HTTPNotFound()
        self.plugin.delete_vifinfo(id)
        return exc.HTTPNoContent()

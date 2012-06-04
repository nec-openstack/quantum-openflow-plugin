# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

from webob import exc

from quantum import wsgi
from quantum.api import api_common as common
from quantum.common import exceptions as qexception
from quantum.extensions import extensions
from quantum.manager import QuantumManager


class Vifinfo(object):

    def __init__(self):
        pass

    @classmethod
    def get_name(cls):
        return "vifinfos"

    @classmethod
    def get_alias(cls):
        return "VIFINFOS"

    @classmethod
    def get_description(cls):
        return "The Virtual Interface - OpenFlow Port Mapping API Extension."

    @classmethod
    def get_namespace(cls):
        return "http://www.nec.co.jp/api/ext/vifinfo/v1.1"

    @classmethod
    def get_updated(cls):
        return "2011-04-05T13:34:20+09:00"

    @classmethod
    def get_resources(cls):
        controller = VifinfosController(QuantumManager.get_plugin())
        return [extensions.ResourceExtension('extensions/nec/vifinfos',
                                             controller)]


class VifinfosController(common.QuantumController, wsgi.Controller):
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
        #if not params['datapath_id']:
        #    raise exc.HTTPBadRequest("No datapath_id.")
        params['port_no'] = ofs_port.get('port_no', None)
        #if not params['port_no']:
        #    raise exc.HTTPBadRequest("No port_no.")
        vlan_id = ofs_port.get('vlan_id', None)
        if vlan_id:
            params['vlan_id'] = vlan_id
        else:
            params['vlan_id'] = 65535
        params['mac'] = ofs_port.get('mac', None)
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
                                params['vlan_id'],
                                params['mac'])
        return {'vifinfo': {'interface_id': params['interface_id']}}

    def _is_same_vifinfo(self, vifinfo, params):
        for key in ['datapath_id', 'port_no', 'vlan_id', 'mac']:
            if ofs_port.get(key, None) != params[key]:
                return False
        return True

    def update(self, request, id):
        vifinfo = self.plugin.get_vifinfo(id)
        params = self._parse_request_params(request)
        self.plugin.update_vifinfo(params['interface_id'],
                                   params['datapath_id'],
                                   params['port_no'],
                                   params['vlan_id'],
                                   params['mac'])
        return exc.HTTPNoContent()

    def delete(self, request, id):
        vifinfo = self.plugin.get_vifinfo(id)
        if not vifinfo:
            raise exc.HTTPNotFound()
        self.plugin.delete_vifinfo(id)
        return exc.HTTPNoContent()

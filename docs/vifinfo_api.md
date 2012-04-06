VIFInfo API Specification (Quantum Extension API)
=================================================


Introduction
------------

VIFInfo is a mapping of Virtual Interface (VIF) to the port on the OpenFlow network.
VIFInfo is needed by this plugin to configure OpenFlow Controller
to specify the binding of the port and the slice(Virtual Network).
Who plugs a VIF to an edge OpenFlow Switch (e.g. VIFDriver at nova-compute),
would create a logical port on Quantum and attache the VIF to the port,
and have to specify where the VIF is pluged on the OpneFlow Network
through this VIFInfo API.

VIFInfo API is implemented as Quantum Extension API.


Concepts
--------

### VIFInfo

VIF is mapped to one OpenFlow port specified with
a OpenFlow Swtich ID and a port number.


Operation List
--------------

<table>
  <tr><th>Operation</th><th>Verb</th><th>URI</th></tr>
  <tr><td>List VIFInfos</td><td>GET</td><td>/vifinfos</td></tr>
  <tr><td>Register VIFInfo</td><td>POST</td><td>/vifinfos</td></tr>
  <tr><td>Delete VIFInfo</td><td>DELETE</td><td>/vifinfos/{VIF ID}</td></tr>
  <tr><td>Show VIFInfo</td><td>GET</td><td>/vifinfos/{VIF ID}</td></tr>
  <tr><td>Update VIFInfo</td><td>PUT</td><td>/vifinfos/{VIF ID}</td></tr>
</table>


List VIFInfo
------------

This operation lists VIFInfo IDs.

### Request

*GET /vifinfos*

This operation does not require a request body.

### Response

Normal Response Code(s): 200-OK

Error Response Code(s): 

Body: { "vifinfos": [ { " interface_id": "<VIF ID >" }, ... ] }

### Example

Request:

        GET /vifinfos

Response:

        {
            "vifinfos":
                [
                    {
                        "interface_id": "92d93f43-8d74-4067-a877-f7462bbb8352"
                    },
                    {
                        "interface_id": "f51d3bee-5d20-45e9-b9d3-487f0882801e"
                    }
                ]
        }


Register VIFInfo
----------------

This operation registers VIFInfo to this plugin.

### Request

*POST /vifinfos*

Body: { "vifinfo": { "interface_id" : "<VIF ID>",
"ofs_port": { "datapath_id": "<Switch ID>",
"port_no": "<Port Number>",
"vlan_id": "<VLAN ID(Option)>" } } }

### Response

Normal Response Code(s): 200-OK

Error Response Code(s): 400-BadRequest

Body: { "vifinfos": { "interface_id": "<VIF ID >" } }

### Example

Request:

        POST /vifinfos

        {
            "vifinfo":
                {
                    "interface_id": "92d93f43-8d74-4067-a877-f7462bbb8352",
                    "ofs_port":
                        {
                            "datapath_id": "0x001A",
                            "port_no": "2"
                        }
                }
        }

Response:

        {
            "vifinfo":
                {
                    "interface_id": "92d93f43-8d74-4067-a877-f7462bbb8352"
                }
        }


Delete VIFInfo
--------------

This operation deletes VIFInfo.

### Request

*DELETE /vifinfos/{VIF ID}*

This operation does not require a request body.

### Response

Normal Response Code(s): 204-NoContent

Error Response Code(s): 404-NotFound

No data returned in response body.

### Example

Request:

        DELETE /vifinfos/92d93f43-8d74-4067-a877-f7462bbb8352


Show VIFInfo
------------

This operation shows VIFInfo.

### Request

*GET /vifinfos/{VIF ID}*

This operation does not require a request body.

### Response

Normal Response Code(s): 200-OK

Error Response Code(s): 404-NotFound

Body: { "vifinfo": { "interface_id" : "<VIF ID>",
"ofs_port": { "datapath_id": "<Switch ID>",
"port_no": "<Port Number>",
"vlan_id": "<VLAN ID>" } } }

### Example

Request:

        GET /vifinfos/92d93f43-8d74-4067-a877-f7462bbb8352

Response:

        {
            "vifinfo":
                {
                    "interface_id": "92d93f43-8d74-4067-a877-f7462bbb8352",
                    "ofs_port":
                        {
                            "datapath_id": "0x001A",
                            "port_no": "2"
                            "vlan_id": "65535"
                        }
                }
        }


Update VIFInfo
--------------

This operation updates VIFInfo.

### Request

*PUT /vifinfos/{VIF ID}*

Body: { "vifinfo": { "interface_id" : "<VIF ID>",
"ofs_port": { "datapath_id": "<Switch ID>",
"port_no": "<Port Number>",
"vlan_id": "<VLAN ID(Option)>" } } }

### Response

Normal Response Code(s): 204-NoContent

Error Response Code(s): 400-BadRequest, 404-NotFound

No data returned in response body.

### Example

Request:

        PUT /vifinfos/92d93f43-8d74-4067-a877-f7462bbb8352

        {
            "vifinfo":
                {
                    "interface_id": "92d93f43-8d74-4067-a877-f7462bbb8352",
                    "ofs_port":
                        {
                            "datapath_id": "0x001A",
                            "port_no": "2",
                            "vlan_id": "100"
                        }
                }
        }

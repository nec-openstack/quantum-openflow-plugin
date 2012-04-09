Filter API Specification (Quantum Extension API)
================================================


Introduction
------------

Filter API provides a primitive firewall for Nova services and admins.
This API exposes the filtering functionality of OpenFlow Controller
in the view of logical resource.

It could be an alternative firewall for Security Group.


Concepts
--------

Filter is associated with a logical network on Quantum,
and can also be associated with a logical port on Quantum.
Filter has a priority, a condition and an action.
A condition can be specified with a logical port on Quantum.


Filter Data Structure
---------------------

Filter must contains a priority, a condition and an action.
A condition contains a logical port on Quantum
 and other l2-l4 parameters as follows:

        {
            "filter":
                {
                    "priority": "<Priority number of this filter rule (1-32766)>",
                    "condition":
                        {
                            "in_port": "<Incoming Logical Port ID on Quantum>",
                            "src_mac": "<Source MAC address>",
                            "dst_mac": "<Destination MAC address>",
                            "src_cidr": "<Source IP address>",
                            "dst_cidr": "<Destination IP address>",
                            "protocol": "<Protocol (arp/tcp/udp/icmp)>",
                            "src_port": "<L4 source port number>",
                            "dst_port": "<L4 destination port number>"
                        },
                    "action": "<Action for matched packets (ACCEPT or DROP)>"
                }
        }


Operation List
--------------

<table>
  <tr><th>Operation</th><th>Verb</th><th>URI</th></tr>
  <tr><td>List Filters</td><td>GET</td>
      <td>/tenants/{Tenant ID}/networks/{Network ID}/filters</td></tr>
  <tr><td>Create Filter</td><td>POST</td>
      <td>/tenants/{Tenant ID}/networks/{Network ID}/filters</td></tr>
  <tr><td>Delete Filter</td><td>DELETE</td>
      <td>/tenants/{Tenant ID}/networks/{Network ID}/filters/{Filter ID}</td></tr>
  <tr><td>Show Filter</td><td>GET</td>
      <td>/tenants/{Tenant ID}/networks/{Network ID}/filters/{Filter ID}</td></tr>
  <tr><td>Update Filter</td><td>PUT</td>
      <td>/tenants/{Tenant ID}/networks/{Network ID}/filters/{Filter ID}</td></tr>
</table>


List Filter
-----------

This operation lists filter IDs.

### Request

*GET /tenants/{Tenant ID}/networks/{Network ID}/filters*

This operation does not require a request body.

### Response

Normal Response Code(s): 200-OK

Error Response Code(s): 401-Unauthorized, 420-NetworkNotFound

The body of this response contains filters as list of IDs.

### Example

Request:

        GET /tenants/demo/networks/cabcc62b-73c1-4fc9-8fc3-ec797e4fe777/filters

Response:

        {
            "filters":
                [
                    {
                        "id": "91cc80a4-1b2f-42f9-abd3-f14f5e0119e2"
                    },
                    {
                        "id": "5b2e487a-74a9-473f-8578-1dde12d32c6a"
                    }
                ]
        }


Create Filter
-------------

This operation creates a filter.

### Request

*POST /tenants/{Tenant ID}/networks/{Network ID}/filters*

The body for this request must contain a filter object specifying a priority,
a condition and an action.
The conditions can be specified with a logical port, and other l2-l4 parameters.
See *Filter Data Structure*.


### Response

Normal Response Code(s): 200-OK

Error Response Code(s): 400-BadRequest, 401-Unauthorized, 420-NetworkNotFound, 430-PortNotFound

The body of this response contains the filter ID.

### Example

Request:

        POST /tenants/demo/networks/cabcc62b-73c1-4fc9-8fc3-ec797e4fe777/filters

        {
            "filter":
                {
                    "priority": "10",
                    "condition":
                        {
                            "dst_mac": "00:4C:00:00:00:01",
                            "src_cidr": "133.0.0.0/8",
                            "dst_cidr": "192.168.1.1/32",
                            "protocol": "tcp",
                            "dst_port": "22",
                        },
                    "action": "ACCEPT"
                }
        }

Response:

        {
            "filter":
                {
                    "id": "91cc80a4-1b2f-42f9-abd3-f14f5e0119e2"
                }
        }


Delete Filter
--------------

This operation deletes Filter.

### Request

*DELETE /tenants/{Tenant ID}/networks/{Network ID}/filters/{Filter ID}*

This operation does not require a request body.

### Response

Normal Response Code(s): 204-NoContent

Error Response Code(s): 401-Unauthorized, 404-NotFound, 420-NetworkNotFound

No data returned in response body.

### Example

Request:

        DELETE /tenants/demo/networks/cabcc62b-73c1-4fc9-8fc3-ec797e4fe777/filters/91cc80a4-1b2f-42f9-abd3-f14f5e0119e2


Show Filter
------------

This operation shows Filter.

### Request

*GET /tenants/{Tenant ID}/networks/{Network ID}/filters/{Filter ID}*

This operation does not require a request body.

### Response

Normal Response Code(s): 200-OK

Error Response Code(s): 401-Unauthorized, 404-NotFound, 420-NetworkNotFound

The body for this response contains filter specifications.
See *Filter Data Structure*.

### Example

Request:

        GET /tenants/demo/networks/cabcc62b-73c1-4fc9-8fc3-ec797e4fe777/filters/91cc80a4-1b2f-42f9-abd3-f14f5e0119e2

Response:

        {
            "filter":
                {
                    "priority": "10",
                    "condition":
                        {
                            "dst_mac": "00:4C:00:00:00:01",
                            "src_cidr": "133.0.0.0/8",
                            "dst_cidr": "192.168.1.1/32",
                            "protocol": "tcp",
                            "dst_port": "22",
                        },
                    "action": "ACCEPT"
                }
        }


Update Filter
--------------

This operation updates filter.

### Request

*PUT /tenants/{Tenant ID}/networks/{Network ID}/filters/{Filter ID}*

The body for this request is the same as the body of *Create Filter* request.

### Response

Normal Response Code(s): 204-NoContent

Error Response Code(s): 400-BadRequest, 401-Unauthorized, 404-NotFound, 420-NetworkNotFound

No data returned in response body.

### Example

Request:

        PUT /tenants/demo/networks/cabcc62b-73c1-4fc9-8fc3-ec797e4fe777/filters/91cc80a4-1b2f-42f9-abd3-f14f5e0119e2

        {
            "filter":
                {
                    "priority": "10",
                    "condition":
                        {
                            "in_port": "548f286b-dcb3-4c8f-a6b9-deb15de5301e",
                            "dst_mac": "00:4C:00:00:00:01",
                            "src_cidr": "133.0.0.0/8",
                            "dst_cidr": "192.168.1.1/32",
                            "protocol": "tcp",
                            "dst_port": "22",
                        },
                    "action": "ACCEPT"
                }
        }

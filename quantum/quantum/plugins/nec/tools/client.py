# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

import httplib
import logging
import socket
from webob import exc

from quantum.client import Client as QuantumClient
from quantum.common import exceptions

LOG = logging.getLogger(__name__)


class Client(QuantumClient):

    def do_request(self, method, action, body=None,
                   headers=None, params=None):
        LOG.debug("Client issuing request: %s %s" % (method, action))

        body = self.serialize(body)
        try:
            connection_type = self.get_connection_type()
            headers = headers or {"Content-Type":
                                      "application/%s" % self.format}
            # Open connection and send request, handling SSL certs
            certs = {'key_file': self.key_file, 'cert_file': self.cert_file}
            certs = dict((x, certs[x]) for x in certs if certs[x] != None)
            if self.use_ssl and len(certs):
                conn = connection_type(self.host, self.port, **certs)
            else:
                conn = connection_type(self.host, self.port)
            res = self._send_request(conn, method, action, body, headers)
            status_code = self.get_status_code(res)
            data = res.read()
            LOG.debug("Reply: status_code = %s, data = [%s]" \
                      % (str(status_code), data))
            if status_code in (httplib.OK,
                               httplib.CREATED,
                               httplib.ACCEPTED,
                               httplib.NO_CONTENT):
                if data and len(data) > 1:
                    return self.deserialize(data, status_code)
            else:
                self._handle_fault_response(status_code, data)
        except (socket.error, IOError), e:
            exc = exceptions.ConnectionFailed(reason=str(e))
            LOG.exception(exc.message)
            raise exc

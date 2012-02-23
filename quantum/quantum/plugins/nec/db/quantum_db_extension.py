# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

from sqlalchemy.orm import exc

import quantum.db.api as db
import quantum.db.models as models


def get_plugged_port(interface_id):
    session = db.get_session()
    try:
        return session.query(models.Port).\
                 filter_by(interface_id=interface_id).one()
    except exc.NoResultFound:
        return None

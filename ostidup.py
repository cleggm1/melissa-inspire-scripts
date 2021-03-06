#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2016 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

""" Bibcheck plugin to delete duplicate info for OSTI from tag
    8564_w/y if in tag 035__a/9
"""

import re

provenance = 'OSTI'

osti_id = re.compile(r'^https?://(?:www\.)?osti\.gov/.*?\D(\d+)$')


def check_record(record):
    """ move 8564_u/y to 035__a/9 """
    for pos, val in record.iterfield('8564_u',
                                     subfield_filter=('y', provenance)):
        if val:
            val = val.replace('%26', '&')
            ostimatch = osti_id.match(val)
            if ostimatch:
                for _, oi in record.iterfield('035__a', subfield_filter=('9', 'OSTI')):
                    if oi == ostimatch.group(1):
                        record.delete_field((pos[0][0:3], pos[1], None))
                        record.set_amended(
                            "removed dup link %s %s" % (record.record_id, val))
                    else:
                        record.warn("different info in 8564_u and 035__a: %s 8564_u:%s 035__a:%s" % (record.record_id, val, oi))


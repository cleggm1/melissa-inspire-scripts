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
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


"""
If a HEPNames record has multiple 'e' subfields in one '693__' field:
split the field, copying the other subfields
"""

from invenio.bibcheck_task import AmendableRecord, add_field
from invenio.bibedit_utils import get_bibrecord
from invenio.search_engine import perform_request_search

test_records = [1477490,1477491,981873]
search = "693__e:/.*/"

def fields_to_split(record, tag, ind1, ind2, sfcode, filter_sf):
    """ Return fields with several [marc] subfields """
    from invenio.bibrecord import record_get_field_instances
    to_split = {}
    for field in record_get_field_instances(record, tag, ind1, ind2):
        parts = []
        rest_before = []
        rest_after = []
        rest = rest_before
        for subfield in field[0]:
            if subfield[0] == sfcode:
                parts.append(subfield)
                rest = rest_after
            else:
                rest.append(subfield)
        if len(parts) > 1:
            to_split[field[4]] = (parts, rest_before, rest_after)
    return to_split


def check_record(record):
    """ Split fields """
    from invenio.bibrecord import record_delete_field
    from invenio.bibrecord import record_add_field

    message = ""
    marc = '693__e'
    tag = marc[:3]
    if not record.has_key(tag):
        continue
    ind1 = marc[3].replace('_', ' ')
    ind2 = marc[4].replace('_', ' ')
    sfcode = marc[5]
    to_split = fields_to_split(record, tag, ind1, ind2, sfcode)

    if not to_split:
        continue
#   work from the back to try to preserve order
    positions = to_split.keys()
    positions.sort(reverse=True)
    for global_pos in positions:
        (parts, rest_before, rest_after) = to_split[global_pos]
        message += " - split %s %s" % (tag, parts)
        record_delete_field(record, tag, ind1, ind2,
                            field_position_global=global_pos)
        parts.reverse()
        for subfield in parts:
            field = rest_before + [subfield, ] + rest_after
            record_add_field(record, tag, ind1, ind2, '', field,
                             field_position_global=global_pos)
    if message:
        record.set_amended(message)


if __name__ == '__main__':
    for record in test_records:
        record = AmendableRecord(get_bibrecord(record))
        record.rule  = {}
        record.rule['name'] = 'melissa'
        record.rule['holdingpen'] = False
        check_record(record)

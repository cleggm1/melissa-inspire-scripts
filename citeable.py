# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2016 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""
Adds 980__a:Citeable to HEP records that have p, v, and c subfields in 773 (excluding proceedings)
"""

from invenio.bibcheck_task import AmendableRecord
from invenio.bibedit_utils import get_bibrecord
from invenio.search_engine import perform_request_search, get_fieldvalues

search = "j:/.*?,.*?,.*/ -980:citeable -980:proceedings"
results = perform_request_search(p=search, cc="HEP")
test_records = [1491292,40552]
citeable_fields = ("773__p", "773__v", "773__c")


def check_record(record):
    pubnote_dict = {}
    citeable_pubnote = False
    for (tag, fieldpos, subfieldpos), val in record.iterfields(citeable_fields):
        if not val.strip():
            continue
        if (fieldpos) in pubnote_dict:
            pubnote_dict[fieldpos].append(tag[5])
        else:
            pubnote_dict[fieldpos] = [tag[5]]
        for k, v in pubnote_dict.items():
            if all(x in v for x in ["p", "v", "c"]):
                print (k, v)
                citeable_pubnote = True
    if citeable_pubnote:
        print "%s: Added 980__a:Citeable" % record.record_id
        record_add_field(record, '980', ' ', ' ', subfields=('a', 'Citeable'))
        record.set_amended("%s: Added 980__a:Citeable" % record.record_id)
 
          


if __name__ == '__main__':
    for r in test_records:
        print "Working on record %i" % r
        record = AmendableRecord(get_bibrecord(r))
        check_record(record)

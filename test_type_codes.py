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

""" Bibcheck plugin to add 980__a type-codes to records from journals that always
   contain published, conference, or review papers
"""

from invenio.search_engine import perform_request_search, get_fieldvalues

#test_records = [1367219, 666513]
test_records = [43747,614,1713,1113,1476529]

JOURNAL_PUBLISHED_DICT = {"Ann.Rev.Astron.Astrophys.":"10.1146/annurev-astro",
"Astrophys.J.":"10.1088/0004-637X/",
"Phys.Lett.":"10.1016/j.physletb."
}
CONFERENCE_DICT = {"AIP Conf.Proc.":None}
REVIEW_DICT = {"Ann.Rev.Astron.Astrophys.":None,
"Phys.Rept.":None}

type_codes = ['Published', 'Review', 'ConferencePaper']

def try_dict(dict):
    if type_code not in codes:
        for key, val in dict.items():
            if key in journals:
                return True
            elif val:
                if any(val in d for d in dois):
                    return True

for record in test_records:
    journals = get_fieldvalues(record, '773__p')
    dois = get_fieldvalues(record, '0247_a')
    codes = get_fieldvalues(record, '980__a')
    for type_code in type_codes:
        if type_code == 'Published':
            if try_dict(JOURNAL_PUBLISHED_DICT):
                print "Adding 980__a:%s to record %i" % (type_code, record)
#                record.add_field('980__', '', subfields=[('a', type_code)]
        if type_code == 'ConferencePaper':
            if try_dict(CONFERENCE_DICT):
                print "Adding 980__a:%s to record %i" % (type_code, record)
#                record.add_field('980__', '', subfields=[('a', type_code)]
        if type_code == 'Review':
            if try_dict(REVIEW_DICT):
                print "Adding 980__a:%s to record %i" % (type_code, record)
#                record.add_field('980__', '', subfields=[('a', type_code)]

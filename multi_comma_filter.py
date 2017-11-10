#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Find authors in HEP records with multiple commas, filtering out suffixes
"""

from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import filter_field_instances, record_get_field_instances
import re
suffixes = ('Sr.', 'Jr.', 'II', 'III', 'IV')

def update(recid):
    record = get_record(recid)
    tags = ('100', '700')
    field_instances = []
    for tag in tags:
        field_instances.append(filter_field_instances(record_get_field_instances(record, tag, '', ''), 'a', commas, filter_mode='r'))
    for field_instance in field_instances:
        for author in field_instance:
            for a in author[0]:
                if a[0] == 'a':
                    commatch = commas.match(a[1])
                    if commatch:
                        if not any(x in commatch.group() for x in suffixes):
                             return (recid, commatch.group())


search = "100__a:',*,*' or 700__a:',*,*'"
auths = []
results = perform_request_search(p=search, cc='HEP')
for r in results:
    tried = update(r)
    if tried:
        auths.append(tried)

with open('commas_to_fix.html', 'w') as output:
    for x in auths:
        output.write('<a href="https://inspirehep.net/record/%i">%s</a><br>\n' % (x[0], x[1]))

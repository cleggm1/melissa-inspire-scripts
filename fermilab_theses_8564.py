#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Looks for HEP records with 8564_y:fermilabthesisf but no 8564_y:Fulltext
Some records have a link to the Fermilab server but no uploaded fulltext
Some have an uploaded text, but it isn't labeled as 'Fulltext'
"""

from invenio.search_engine import perform_request_search, get_fieldvalues, get_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
record_add_field
import re

test_records = []
test_records = [14003]

#upload_string = re.compile(r'^https?://(?:www\.)?inspirehep\.net/record/.*?fermilab-thesis-\d+-\d+-\.pdf$')

def create_xml(recid):
    correct_record = {}
    tag = '8564_'
    record = get_record(recid)
    flag = None
    record_add_field(record, '001', controlfield_value=str(recid))
    field_instances = record_get_field_instances(record, tag[0:3], tag[3], tag[4])
    correct_subfields = []
    for field_instance in field_instances:
        correct_subfields = []
#        print field_instance
        for c,v in field_instance[0]:
#            print c,v
            matchObj = re.search(r'inspirehep\.net/record/\d+/files/fermilab-thesis-.*?\.pdf', v, flags=re.IGNORECASE)
            if matchObj:
                print 'yes'
                flag = True
                correct_subfields.append(('y', 'Fulltext'))
            correct_subfields.append((c,v))
        record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
            subfields=correct_subfields)
    if flag:
        return print_rec(correct_record)
    else:
        return None
def main():
    update_counter = 0
    filter_pattern = "8564_y:fermilabthesisf -8564_y:Fulltext"
    results = perform_request_search(p=filter_pattern, cc="HEP")
    with open(re.sub('.py', '_correct.out', 'tmp_'+__file__), 'w') as output:
        output.write('<collection>')
#        for r in test_records:
        for r in results:
            update = create_xml(r)
            if update:
                update_counter += 1
                output.write(update)
        output.write('</collection>')
    print "%i of %i records will be updated" % (update_counter, len(results))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

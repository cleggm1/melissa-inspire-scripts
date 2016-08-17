#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Replaces old aff with new aff. If specified affiliation(s) already in field, 
the old aff will be deleted without adding a new aff
"""

from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
record_add_field
import re

old_aff = 'Lebedev Res. Ctr. Phys., Moscow'
new_aff = 'LPI, Moscow (main)'
skip_aff = ['Lebedev Inst.']
VERBOSE = True
VERBOSE = False

def create_xml(recid, old_aff=None, new_aff=None, skip_aff=None):
    record = get_record(recid)
    correct_record = {}
    tags = ('100__', '700__')
    record_add_field(correct_record, '001', controlfield_value=recid)
    for tag in tags:
        field_instances = record_get_field_instances(record, \
                                                     tag[0:3], tag[3], tag[4])
        for field_instance in field_instances:
            correct_subfields = []
            skip_aff_exists = False
            for aff in skip_aff:
                if any(val for code, val in field_instance[0] if aff in val):
                    skip_aff_exists = True
                    if VERBOSE:
                        print "%s exists, deleting %s" % (aff, old_aff)
            if skip_aff_exists:
                for code, value in field_instance[0]:
                    if code == 'u':
                        if value != old_aff:
                            correct_subfields.append((code, value))
                    else:
                        correct_subfields.append((code, value))
            else:
                for code, value in field_instance[0]:
                    if code == 'u':
                        if value == old_aff:
                            correct_subfields.append((code, new_aff))
                            if VERBOSE:
                                print "Changing %s to %s" % (old_aff, new_aff)
                        else:
                            correct_subfields.append((code, value))
                    else:
                        correct_subfields.append((code, value))
            record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
                             subfields=correct_subfields)
    return print_rec(correct_record)

def main():
    matchObj = re.match('^(\s)',old_aff)
    if matchObj:
        filename = "tmp_" + matchObj.group(1) + "_correct.out"
    else:
        filename = "tmp_" + re.sub('.py', '_correct.out', __file__)
    output = open(filename, 'w')
    search = '"Lebedev Res. Ctr. Phys., Moscow"'
    results = perform_request_search(p = search, cc = 'HEP')
    if len(results) > 0:
        output.write("<collection>")
        for r in results:
            if VERBOSE:
                print "Working on", r
            update = create_xml(r, old_aff, new_aff, skip_aff)
            if update:
                output.write(update)
        output.write("</collection>")
    output.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting' 

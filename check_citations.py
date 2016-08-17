#!/usr/bin/python
# -*- coding: utf-8 -*-

from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import record_get_field_instances
import re

VERBOSE = True
TEST = True
TEST = False
search = '999C5s:"PTEP*" -999C5s:/^PTEP,20[0-9]{2},([0-9]{2,3}[A-Z][0-9]+|[0-9]{6})$/'
if TEST:
    search = 'recid:1477028'
journal = 'PTEP'
tag = '999C5'
recids = []

   

def main():
    matchObj = re.match('^(\s)', journal)
    if matchObj:
        filename = 'tmp_' + matchObj.group(1) + '_' + re.sub('.py', '.html', __file__)
    else:
        filename = 'tmp_' + re.sub('.py', '.html', __file__)
    if TEST:
        print "Testing mode...."
    else:
        print "Checking records in this search: %s" % search
    check_these_records = []
    x = perform_request_search(p=search, cc='HEP')
    if len(x) > 0:
        if VERBOSE:
            print "%i records in search" % len(x)
        output = open(filename,'w')
        for r in x:
            if VERBOSE:
                print "Working on record %i" % r
            record = get_record(r)
            ptep_field_instances = []
            field_instances = record_get_field_instances(record, \
  		tag[0:3], tag[3], tag[4])
            for field_instance in field_instances:
#                if TEST:
#                    print "field_instance: ", field_instance
                for (code, value) in field_instance[0]:
                    if journal in value:
                        if TEST:
                            print "suspect field_instance[0]: ", field_instance[0]
                        ptep_field_instances.append(field_instance[0])
            for item in ptep_field_instances:
                if any('r' in code for code in item) or any('0' in code for code in item):
                    if TEST:
                        print "'r' or '0' in item:", item
                else:
                    if VERBOSE:
                        print "Found a record that needs checking: %i" % r
                    check_these_records.append(r)
        if check_these_records:
            check_these_records = sorted(set(check_these_records))
            if VERBOSE:
                print "%i records of %i total in search should be checked" % (len(check_these_records), len(x))
            check_these_records = ['<a href="https://inspirehep.net/record/edit/?ln=en#state=edit&recid=%i">%i</a><br />' % (r,r) for r in check_these_records]
            output.writelines(check_these_records)
        output.close()                
    else:
        if VERBOSE:
            print "No results in search"

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'


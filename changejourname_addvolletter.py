"""Searches INSPIRE-HEP for records with the 'old journal' pubnote,
   changes them to the 'new journal' pubnote, and adds the journal letter to the volume if necessary.
"""
#!/usr/bin/python
# -*- coding: utf-8 -*-

from invenio.search_engine import perform_request_search, get_record, get_fieldvalues
from invenio.bibrecord import print_rec, record_get_field_instances, \
record_add_field
import re
from pickle import dump

VERBOSE = True
TEST = False
filepath = '/user/m/mclegg/misc/'
test_jour = [1514919, 755721, 733726]
test_refs = [1603128, 1602605]
old_journal = 'Europhys.Lett.'
repl_journal = 'EPL'
vol_change = 77
vol_curr = 117 + 1

def create_xml773(recid):
    record = get_record(recid)
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    field_instances = record_get_field_instances(record, '773', '', '')
    correct_subfields = []
    for field_instance in field_instances:
        correct_subfields = []
#        print field_instance[0]
        for code, value in field_instance[0]:
            if code == 'p' and value == old_journal:
                correct_subfields.append(('p', repl_journal))
                if VERBOSE:
                    print "%s: Replacing 773__p %s with %s" % (recid, value, repl_journal)
            else:
                correct_subfields.append((code, value))
        record_add_field(correct_record, '773', '', '',
                             subfields=correct_subfields)
    return print_rec(correct_record)

def create_xmlrefs(recid):
    subrefs = ['%s,%i,' % (old_journal, x) for x in range(vol_change, vol_curr)]
    record = get_record(recid)
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    field_instances = record_get_field_instances(record, '999', 'C', '5')
    correct_subfields = []
    for field_instance in field_instances:
        correct_subfields = []
        for code, value in field_instance[0]:
            if code == 's' and any(x for x in subrefs if x in value):
                newval = re.sub(old_journal, repl_journal, value)
                if VERBOSE:
                    print "%s: Replacing %s with %s" % (recid, value, newval)
                correct_subfields.append(('s', newval))
            else:
                correct_subfields.append((code, value))
        record_add_field(correct_record, '999', 'C', '5',
                             subfields=correct_subfields)
    return print_rec(correct_record)

def main():
    updated = []
    file_name773 = "%stmp_%s_773_correct.xml" % (file_path, repl_journal)
    file_namerefs = "%stmp_%s_refs_correct.xml" % (file_path, repl_journal)
    with open(file_name773,'w') as output773:
        output773.write('<collection>')
        if TEST:
            for record in test_jour:
                output773.write(create_xml773(record))
                updated.append(record)
        else:
            for vol in range(vol_change, vol_curr):
                search = 'fin j "%s,%i,*"' % (old_journal, vol)
                x = perform_request_search(p=search, cc="HEP")
                if VERBOSE:
                    print "Searching for %s" % search
                if len(x) > 0:
                    if VERBOSE:
                        print "Replacing 773__p of %d records with %s" % (len(x), repl_journal)
                    for record in x:
                        output773.write(create_xml773(record))
                        updated.append(record)
        output773.write('</collection>')
    with open(file_namerefs, 'w') as outputrefs:
        outputrefs.write('<collection>')
        if TEST:
            for record in test_refs:
                update = create_xmlrefs(record)
                if update:
                    outputrefs.write(update)
                    updated.append(record)
        else:
            search = '999C5:"%s,*"' % old_journal
            x = perform_request_search(p=search, cc="HEP")
            if VERBOSE:
                print "Searching for %s" % search
            if len(x) > 0:
                for record in x:
                    update = create_xmlrefs(record)
                    if update:
                        outputrefs.write(update)
                        updated.append(record)
        outputrefs.write('</collection>')

    with open('%sto_index.out' % filepath, 'wb') as to_index:
        dump(updated, to_index)
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'    

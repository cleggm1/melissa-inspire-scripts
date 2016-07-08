#!/usr/bin/python
# -*- coding: utf-8 -*-

from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field
import re, math

Test = False
VERBOSE = True
ID_dict = {}

def create_xml(recid, IDs, tags):
    """
    Replaces specific inspire-ids in records with nothing
    """
    if VERBOSE:
        print "Working on %s" % recid
    record = get_record(int(recid))
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=recid)
    for tag in tags:
        field_instances = record_get_field_instances(record, \
                                                     tag[0:3], tag[3], tag[4])
        for field_instance in field_instances:
            correct_subfields = []
            for code, value in field_instance[0]:
                if code == 'i':
                    if value in IDs:
                        if VERBOSE:
                            print "Getting rid of %s from %s!" % (value, recid)
                        pass
                    else:
                        correct_subfields.append((code, value))
                else:
                    correct_subfields.append((code, value))

            record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
                             subfields=correct_subfields)
    return print_rec(correct_record)

def main():
    input = open('dupIDs.in', 'r').readlines()
    if Test:
        input = ['000884120 700__ $$aKoenig, Sebastian$$iINSPIRE-00320516$$uMainz U.',
    '000884120 700__ $$aKonig, Stefan$$iINSPIRE-00320516$$uFreiburg U.',
    '000884120 700__ $$aCrupi, Roberto$$iINSPIRE-00212936$$uINFN, Lecce$$uSalento U.',
    '000884120 700__ $$aCrepe-Renaudin, Sabine$$iINSPIRE-00212936$$uLPSC, Grenoble']
    for line in input:
        matchObj = re.search(r'^(\d+)\s.*\$\$i(INSPIRE-\d+)\$', line)
        if matchObj:
            recid = matchObj.group(1).lstrip('0')
            ID = matchObj.group(2)
            if recid in ID_dict:
                if ID in ID_dict[recid]:
#                    if VERBOSE:
#                        print "%s already exists for %s" % (ID, recid)
                else:
                    ID_dict[recid].append(ID)
#                    if VERBOSE:
#                         print "Appending %s to %s" % (ID, recid)
            else:
                ID_dict[recid] = [ID]
#                if VERBOSE:
#                    print "Creating entry for %s with %s" % (recid, ID)


    ID_tuples = ID_dict.items()
    dict_sect = int(math.ceil(len(ID_tuples)/10))
    if VERBOSE:
#        print ID_dict
        print "%i records affected, %i output files will be created" % (len(ID_tuples), dict_sect)
    
    files = [open('tmp_remove_IDs_correct%i.out' %i, 'w') for i in range(1,dict_sect+1)]
    for j in range(1,dict_sect+1):
        if VERBOSE:
            print "j is %i" % j
        files[j-1].write('<collection>')
        if j < dict_sect:
            if VERBOSE:
                print "Working on indexes %i-%i of ID_tuples, to be output to file %i" % ((j-1)*10, (j*10)-1, j)
            for key, val in ID_tuples[(j-1)*10:(j*10)]:
                update = create_xml(key, val, ['100__','700__'])
                if update :
                    files[j-1].write(update)
                else:
                    print "Test"
        elif j == dict_sect:
             if VERBOSE:
                print "Working on indexes %i-%i of ID_tuples, to be output to file %i" % ((j-1)*10, len(ID_tuples)-1, j)
             for key, val in ID_tuples[(j-1)*10:]:
                update = create_xml(key, val, ['100__','700__'])
                if update :
                    files[j-1].write(update)
                else:
                    print "Test"

        files[j-1].write('</collection>')
    for f in files:
        f.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'  

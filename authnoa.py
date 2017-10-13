# coding: utf-8
from pickle import load, dump
from invenio.bibrecord import print_rec, record_add_subfield_into, record_delete_field, record_get_field_instances
from invenio.search_engine import get_fieldvalues, get_record, perform_request_search

test_records = [919982, 921328, 920000, 1492395, 920420]
TEST = True

def create_xml(recid, fname=None, oaff=None):
    affs = [a for a in oaff]
    record = get_record(recid)
    auth_location = record_get_field_instances(record, '100', '', '')[0][4]
    record_delete_field(record, '700', '', '')
    for x in affs:
        record_add_subfield_into(record, '100', 'u', x, field_position_global=auth_location)
    return print_rec(record)

def main():
   done_recids = []
#   with open('authnoaff_done_recs.list', 'rb') as done_in:
#       done_recids = load(done_in)
   if TEST:
       left_recids = test_records
       print left_recids
   else:
       with open('authnoaff_todo_recs.list', 'rb') as input:
           left_recids = load(input)
   output = open('tmp_authnoaff_replace.out', 'w')
   output.write('<collection>')
   for r in left_recids:
       first_author_name = get_fieldvalues(r, '100__a')
       first_author_affs = get_fieldvalues(r, '100__u')
       other_authors_names = get_fieldvalues(r, '700__a')
       other_authors_affs = get_fieldvalues(r, '700__u')
#       print first_author_name, first_author_affs, other_authors_names, other_authors_affs
       if len(first_author_name) == 1 and len(other_authors_names) == 0 and len(first_author_affs) == 0:
           found_aff = True
           for x in other_authors_affs:
               aff_search = perform_request_search(p='110__u:"%s"' % x, cc='Institutions')
               if len(aff_search) != 1:
                   found_aff = False
           if found_aff:
               update = create_xml(r, fname=first_author_name, oaff=other_authors_affs)
               if update:
                   print 'yes'
                   output.write(update)
                   done_recids.append(r)
                   print r, 'moving', other_authors_affs, 'to', first_author_name
   output.write('</collection>')
   output.close()
   print '%i of %i records to be corrected' % (len(done_recids), len(left_recids))
   left_recids = list(set(left_recids)-set(done_recids))
   with open('authnoaff_done_recs.list', 'wb') as doneout:
        dump(done_recids, doneout)
   with open('authnoaff_todo_recs.list', 'wb') as todoout:
        dump(left_recids, todoout)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

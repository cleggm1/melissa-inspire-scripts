from invenio.search_engine import perform_request_search, get_record, get_fieldvalues
from invenio.bibrecord import print_rec, record_get_field_instances, \
record_add_field

old_journal = "Stud.Hist.Philos.Mod.Phys."
repl_journal = "Stud.Hist.Phil.Sci."
volume_letter = "B"
tag = "773__"

def create_xml(recid):
    record = get_record(recid)
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    field_instances = record_get_field_instances(record, tag[0:3],
                                                     tag[3], tag[4])
    correct_subfields = []
    for field_instance in field_instances:
        correct_subfields = []
        for code, value in field_instance[0]:
            if code == 'p':
                correct_subfields.append(('p', repl_journal))
            elif code == 'v':
                volume = get_fieldvalues(recid, '773__v')
                for v in volume:
                    new_volume = volume_letter + v
                correct_subfields.append(('v', new_volume))
            else:
                correct_subfields.append((code, value))
        record_add_field(correct_record, tag[0:3], tag[3], tag[4],
                             subfields=correct_subfields)
    return print_rec(correct_record)

def main():
    file_name = "tmp_%s%s_correct.xml" % (repl_journal, volume_letter)
    output = open(file_name,'w')
    search = '773__p:"%s"' % old_journal
    x = perform_request_search(p=search, cc="HEP")
    if len(x) > 0:
        output.write('<collection>')
        for record in x:
           output.write(create_xml(record))
        output.write('</collection>')
    else:
        print "No records in search."    
    output.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'    

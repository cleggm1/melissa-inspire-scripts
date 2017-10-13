# coding: utf-8
from invenio.refextract_api import extract_references_from_string
from invenio.docextract_record import BibRecord
from invenio.bibrecord import print_rec, record_add_field
from invenio.search_engine import get_fieldvalues, perform_request_search
from pickle import load, dump
import re

TEST = False

term_dict = {'wkshp': 'workshop',
'symp': 'symposium',
#'sympos': 'symposium',
'phys': 'physics',
'mtg': 'meeting',
'conf': 'conference',
'accel': 'accelerator',
'colloq': 'colloquium',
'inst': 'institute',
'proc': 'proceedings',
'sem': 'seminar'
}
yearvol = (u'Izv.Vuz.Fiz.', u'Prib.Tekh.Eksp.', u'Vestn.Mosk.Univ.Ser.III Fiz.Astron.', u'Vestn.Leningrad.Univ.Fiz.Khim.',
u'Spektrum Wiss.', u'Bild.Wiss.', u'Phys.Today', u'Izv.Akad.Nauk Uzb.SSR')


def split_ref(text=None):
    if text is None:
        return None
    if 'TRANSL.' in text:
        return None
    nummatchobj = re.search('No\.\s?(\d+)', text, flags=re.IGNORECASE)
    out = []
    uzb = 'Izv.Akad.Nauk Uzb.SSR'
    vals = extract_references_from_string(text).find_subfields('999C5s')
    years = extract_references_from_string(text).find_subfields('999C5y')
    if vals and years:
        y = re.sub('[^0-9]', '', years[0].value)
        splitvals = vals[0].value.split(',')
        if uzb in text:
            splitvals[0] = uzb
        if splitvals[0] in yearvol:
            out.append([('y',y),('p',splitvals[0]),('n',splitvals[1]),('v',y),('c',splitvals[2])])
        elif nummatchobj:
            out.append([('y',y),('p',splitvals[0]),('n',nummatchobj.group(1)),('v',splitvals[1]),('c',splitvals[2])])
        else:
            out.append([('y',y),('p',splitvals[0]),('v',splitvals[1]),('c',splitvals[2])])
    return out

def jcreate_xml(recid, pubnotes):
    record = {}
    record_add_field(record, '001', controlfield_value=str(recid))
    for p in pubnotes:
        record_add_field(record, '773', '', '', subfields=p)
    return print_rec(record)

def ccreate_xml(recid, rawstring):
    found = False
    record = {}
    record_add_field(record, '001', controlfield_value=str(recid))
    rawstring = rawstring.lower().replace('proc. of the', '').replace('proc. of', '').replace('.', ' ').replace('(', '').replace(')', '').replace(' -', '')
    for k,v in term_dict.items():
        if k in rawstring:
            rawstring = rawstring.replace(k,v)
    matchobj = re.search('(.*?\d{4})', rawstring)
    if matchobj:
        search = perform_request_search(p=matchobj.group(), cc='Conferences')
        if len(search) == 1:
            for s in search:
                cnums = get_fieldvalues(s, '111__g')
                cnum = cnums[0]
                existing_cnum = get_fieldvalues(recid, '773__w')
                if cnum not in existing_cnum:
                    print recid, cnum
                    found = True

    if found:
        record_add_field(record, '773', '', '', subfields=[('w', cnum)])
        return print_rec(record)

def main():
    counter = 0
    input_list = []
    done_recids = []
    to_index = []
    with open('pubnote_extract_done_recs.list', 'rb') as recsin:
        done_recids = load(recsin)
    with open('xcontent.txt', 'r') as input:
        for line in input.readlines():
            matchobj = re.search('(\d+)\t(.*)', line)
            try:
                recid = matchobj.group(1)
                rawref = matchobj.group(2)
                if recid not in done_recids:
                    input_list.append((recid,rawref))
            except:
                pass
    output = open('tmp_added_pubnotes.append.out', 'w')
    output.write('<collection>')
    for r, x in input_list:
        if counter < 101:
            jparsed = split_ref(text=x)
            if jparsed:
                print r, jparsed
                jupdate = jcreate_xml(r, jparsed)
                if jupdate:
                    output.write(jupdate)
                    counter += 1
                    done_recids.append(r)                
                    to_index.append(r)
#            else:
            if TEST:
                found_w = get_fieldvalues(r, '773__w')
                if len(found_w) > 0:
                    cupdate = ccreate_xml(r, x)
                    if cupdate:
                        output.write(cupdate)
                        counter += 1
                        done_recids.append(r)
                        to_index.append(r)
        else:
            break
    output.write('</collection>')
    output.close()
    with open('pubnote_extract_done_recs.list', 'wb') as recsout:
        dump(done_recids, recsout)
    with open('pubnote_extract_to_index.list', 'wb') as indexout:
        dump(to_index, indexout)
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

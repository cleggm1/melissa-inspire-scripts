from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibrecord import print_rec, record_add_field
from afftranslator2 import *

import xml.etree.ElementTree as ET
import glob
import re

TEST = True
VERBOSE = False
DEBUG = False
INPUT_COUNTER = 1
OUTPUT_COUNTER = 501



DOCUMENT = 'tmp_osti_lattice.xml'

def get_aff(aff):
    bm = bestmatch(aff,'ICN')
    a = bm[0]
    affNew = a[1]
    affNew = re.sub(';', '</subfield><subfield code="u">', affNew)
    if affNew == 'American Astron. Society':
        affNew = 'APS, New York'
    return affNew

#def get_aff(affiliations):
#    t = re.sub(r'[.,]', '', affiliations)
#    print t
#    x = perform_request_search(p=t, cc='Institutions')
#    print x
#    if len(x) == 1:
#        aff_ICN = get_fieldvalues(x[0], '110__u')
#        return aff_ICN
#    elif len(x) > 1:
#        print 'too many matches for', affiliations
#    elif len(x) < 1:
#        print affiliations, 'could not be found'


def create_xml(input_dict):
    """
    The function create_xml takes an article dictionary from ADS and
    checks to see if it has information that should be added to INSPIRE.
    If so, it builds up that information.
    """
#    print input_dict



    record = {}
    title = [('a', input_dict['title']), ('9', 'OSTI')]
    record_add_field(record, '245', '', '', subfields=title)
    doi = [('a', input_dict['doi']), ('2', 'DOI')]
    record_add_field(record, '024', '7', '', subfields=doi)
    date = [('c', input_dict['date'])]
    record_add_field(record, '269', '', '', subfields=date)
    note = [('h', input_dict['note']), ('9', 'authors')]
    record_add_field(record, '520', '', '', subfields=note)
    collection = [('a',input_dict['collection'])]
    record_add_field(record, '980', '', '', subfields=collection)
    type = [('t', input_dict['type'])]
    record_add_field(record, '336', '', '', subfields=type)
    for i in input_dict['subject']:
#        print i
        subject = [('a', i), ('9', 'OSTI')]
        record_add_field(record, '653', '1', '', subfields=subject)
    firstauthor = [('a', input_dict['firstauthor'][0]), \
                   ('u', input_dict['firstauthor'][1]), \
                   ('v', input_dict['firstauthor'][2])]
    record_add_field(record, '100', '', '', subfields=firstauthor)
    for i in input_dict['otherauthors']:
#        print i
        otherauthors = [('a', i[0]), ('u', i[1]), ('v', i[2])]
        record_add_field(record, '700', '', '', subfields=otherauthors)
#    for key in record:
#        print key, record[key]
#    print record
    return print_rec(record)


#    if TEST:
#        print "In create_xml"
#        print input_dict
#    elements = ['title', 'doi', 'date', 'type', 'subject']
#    element_dict = {}
#    for element in elements:
#        element_dict[element] = ''
#        if element in input_dict:
#            element_dict[element] = input_dict[element]
#    for element in input_dict:
#        print element, input_dict[element]

def long_name(name):
    return '{http://purl.org/dc/elements/1.1/}' + name


def main():
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    tree = ET.parse(DOCUMENT)
    root = tree.getroot()
    input_counter  = 1
    output_counter = 1
    for child in root:
        title = child.find('record').find(long_name('title')).text
        creator = child.find('record').find(long_name('creator')).text
        subjectRelated = child.find('record').find(long_name('subjectRelated')).
text
        description = child.find('record').find(long_name('description')).text
        date = child.find('record').find(long_name('date')).text
        type = child.find('record').find(long_name('type')).text
        relation = child.find('record').find(long_name('relation')).text
        doi = child.find('record').find(long_name('doi')).text
        ostiId = child.find('record').find(long_name('ostiId')).text

        lat_dict = {'title': title, 'type': type, 'doi': doi, 'collection': 'DAT
A', 'date': date}
        if creator:
            #print creator
            match_obj = re.search(r'(.*?)\s\[(.*?)\];', creator)
            if match_obj:
                firstauthorname = match_obj.group(1)
                firstaffiliation = match_obj.group(2)
                #print 'first author = ', firstauthorname
                #print 'first author\'s affiliation = ', firstaffiliation
                firstICN_aff = get_aff(firstaffiliation)
#                firstICN_aff = firstaffiliation
            match_obj = re.findall(r';\s(.*?)\s\[(.*?)\]', creator)
            otherauthors_list = []
            for x in match_obj:
                authorname = x[0]
                affiliation = x[1]
                #print authorname
                #print affiliation
                ICN_aff = get_aff(affiliation)
#                ICN_aff = affiliation
                #print 'ICN_aff =', ICN_aff
                otherauthors_list.append((authorname, ICN_aff, affiliation))
            lat_dict['otherauthors'] = otherauthors_list
        lat_dict['firstauthor'] = (firstauthorname, firstICN_aff, firstaffiliati
on)
        cited_author = firstauthorname.split(' ')
        if '.' not in cited_author[1]:
            cited_author[1] = cited_author[1][0]+'.'
        if cited_author[2]:
            if '.' not in cited_author[2]:
                cited_author[2] = cited_author[2][0]+'.'
        else:
            pass
        cited_author = ' '.join(cited_author)
        #print 'cited_author =', cited_author

        subject = subjectRelated.split('; ')
        lat_dict['subject'] = subject
        #print subject
        match_obj = re.search(r'(\d{4})-\d{2}-\d{2}', date)
        year = match_obj.group(1)
        #print 'year = ', year

        cite_as = description + '<br /><br /><b>Cite as: </b>' + cited_author +
\
                  ' et al. (' + year + ') ' + title + 'doi: <a href="' + doi + '
">' \
                  + doi + '</a><br /><br />'
        lat_dict['note'] = cite_as
        record_update = create_xml(lat_dict)

        output.write(record_update)
        output_counter += 1
       # print 'cite_as =', cite_as
        #if input_counter < INPUT_COUNTER:
         #   input_counter  += 1
        #else:
         #   if output_counter == OUTPUT_COUNTER: break
          #  if child.attrib:
                #print 'child.attrib =', child.attrib
                #record_update = create_xml(child.attrib)
           #     if record_update:
            #        try:
             #           if DEBUG == 1:
              #              print record_update
               #         else:
#                            output.write(record_update)
 #                           output_counter += 1
                #    except:
                 #       print 'CANNOT print record', child.attrib
    output.write('</collection>')
    output.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'


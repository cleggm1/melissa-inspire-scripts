"""
Script for matching INSPIRE dois with no arXiv pre-print with preprints in ADS
http://ads.harvard.edu/pubs/arXiv/ADSmatches.xml
"""

from invenio.bibformat_engine import BibFormatObject
from invenio.search_engine import perform_request_search, get_fieldvalues
import xml.etree.ElementTree as ET
import collections

#DIRECTORY = '/afs/cern.ch/project/inspire/TEST/hoc/'
DIRECTORY = ''
DOCUMENT = DIRECTORY + 'ADSmatches.xml'


def check_doi(input_dict, records_dict, eprints):
    elements = ['doi', 'preprint_id']
    element_dict = {}
    for element in elements:
        element_dict[element] = ''
        if element in input_dict:
            element_dict[element] = input_dict[element]
    eprint        = element_dict['preprint_id']
    doi           = element_dict['doi']
#    if len(perform_request_search(p='eprint:%s' % eprint, cc='HEP')) > 0:
#        return None
    if eprint in eprints:
         return (None, eprint, doi)
    else:
        for r, d in records_dict.items():
            for ds in d.values():
                if any(i == doi for i in ds):
                    return (r, eprint, doi)
                else:
                    return None        


def get_eprint_id(recid):
    """ Find the arxiv number from an INSPIRE record """
    osti_id = None
    for item in BibFormatObject(int(recid)).fields('037__'):
        if item.has_key('9') and item.has_key('a'):
            if item['9'].lower() == 'arxiv':
                arxiv_id = item['a']
    return arxiv_id        

def main():
    counter = 0
    filename = 'ADS_eprints_missing_in_INSPIRE.csv'
    mismatch_filename = ''ADS_eprints_missing_in_INSPIRE_mismatch.csv'
    output = open(filename, 'w')
    mismatch_output = open(mismatch_filename, 'w')
    records = collections.defaultdict(dict)
    search = '0247_2:doi -037__9:arxiv'
    results = perform_request_search(p=search, cc='HEP')
    for r in results:
        doi = get_fieldvalues(r, '0247_a')
        if doi:
            records[r]['doi'] = doi
    eprints = []
    eprint_search = perform_request_search(p='037__9:arxiv', cc='HEP')
    for e in eprint_search:
         eprint = get_eprint_id(e)
         if eprint:
             eprint = eprint.replace('arxiv:', '')
             eprints.append(eprint)
    tree = ET.parse(DOCUMENT)
    root = tree.getroot()
    for child in root:
        if counter < 10:
            if 'doi' and 'preprint_id' in child.attrib:
                found_eprint = check_doi(child.attrib, records, eprints)
                if found_eprint:
                    if found_eprint[0] is True:
                        counter+=1
                        output.write('%s,%s,%s\n' % (found_eprint[0], found_eprint[1], found_eprint[2]))
                    else:                        
                        mismatch_output.write('%s,%s,%s\n' % (found_eprint[0], found_eprint[1], found_eprint[2]))
    output.close()
    print counter

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'


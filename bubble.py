#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Perform HEP search on published only. For each record, get author list, citations/year total, citations/year by hep-th or hep-ex, citations/year from specific journals (make a dictionary 

of Q1, Q2, Q3, Q4 journals). From author list, figure out who are the phd students of each author. Then get cites/year excluding self-cites by the authors or by their 1st gen phd 

students. Then calculate average cites/year by hep-th or by hep-ex. Output everything in csv file.


get_citers_log seems to count citations by when they are added to INSPIRE, not by what year the citation comes from



authorlist -> get name?, pid, figure out who their students are, get all citations by them and their students
"""



from invenio.search_engine import perform_request_search, get_fieldvalues
from invenio.bibauthorid_dbinterface import get_personid_signature_association_for_paper
import re

#search_term = "collection:published ('large nc' or 'large n-c' or 'large n c')"
search_term = "SUSY collection:published"

JOURNALS = {'Phys.Rev.': 'Q1',
            'Prog.Part.Nucl.Phys.': 'Q1'
            }
PAPERS = {}
           

def get_fieldcode(recid):
    codes = get_fieldvalues(recid, '65017a')
    if 'Experiment-HEP' in codes:
        return 'hep-ex'
    if 'Theory-HEP' in codes:
        return 'hep-th'


def get_date(recid):
    year_string = re.compile('\d{4}')
    try_date =  get_fieldvalues(recid, '260__c')
    if len(try_date) == 0:
        try_date = get_fieldvalues(recid, '269__c')
    if len(try_date) == 0:
        return None
    else:
        date = re.match(year_string, try_date[0])
        if date:
            return int(date.group())
        else:
            return None

def main():
    search = perform_request_search(p=search_term, cc='HEP')
    for r in search:
        PAPERS[r] = {'Authors':{}, 'Citation logs':{'Including self-cites':{'Total':{}, 'HEP-EX':{}, 'HEP-TH':{}}, 'Excluding self-cites':{'Total':{}, 'HEP-EX':{}, 'HEP-TH':{}}}}



# Get pids for authors of a paper. Is there a way to associate a pid with an author name?
        PAPERS[r]['Authors'] = {'Person IDs': [val for _, val in get_personid_signature_association_for_paper(r).iteritems()]}

# Get total citations of paper
        cite_search = perform_request_search(p='refersto:recid:%i collection:published ' % r, cc='HEP')
        for r in cite_search:
            date = get_date(r)
            PAPERS[r]['Citation logs']['Including self-cites']['Total'] = {r: date}
# Get all hep-ex citations of paper
            fieldcode = get_fieldcode(r)
            if fieldcode == 'hep-ex':
                PAPERS[r]['Citation logs']['Including self-cites']['HEP-EX'] = {r: date}
            elif fieldcode == 'hep-th':
                PAPERS[r]['Citation logs']['Including self-cites']['HEP-TH'] = {r: date}


# Get citations excluding self-citations of paper
        cite_search = perform_request_search(p='referstox:recid:%i collection:published' % r, cc='HEP')
        
    


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2016 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""
bibcheck plug-in to add OSTI ID to HEP records with a corresponding DOI
"""

import re
from invenio.search_engine import perform_request_search, get_fieldvalues, get_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
record_add_field
from invenio.bibformat_engine import BibFormatObject
#from invenio.bibcheck_task import AmendableRecord
#from invenio.bibedit_utils import get_bibrecord

def create_xml(recid=None, osti_id=None, doi=None):
    osti_exists = False
    doi_exists = False
    osti_mismatch = False
    mismatches = []
    osti_subfields = [('9', 'OSTI'), ('a', osti_id)]
    record = get_record(recid)
    record_link = '<a href="http://inspirehep.net/record/%s">%s</a>' % (str(recid),str(recid))
    append_record = {}
    additions = False
    errors = None
    for item in BibFormatObject(recid).fields('035__'):
        if item.has_key('9') and item.has_key('a'):
            if item['9'] == 'OSTI' and item['a'] == osti_id:
                osti_exists = True
            elif item['9'] == 'OSTI' and item['a'] != osti_id:
                osti_mismatch = True
                mismatches.append(item['a'])
    for item in BibFormatObject(recid).fields('0247_'):
        if item.has_key('2') and item.has_key('a'):
            if item['2'] == 'DOI' and item['a'] == doi:
                doi_exists = True
    if osti_exists is False and osti_mismatch is True:
        print str(recid), "already has a different OSTI ID"
        errors = "doi %s in record %s should match OSTI ID %s, but the record already contains OSTI ID(s) %s<br />" % (doi, record_link, osti_id, ','.join(mismatches))
        return errors
    if doi_exists is False and osti_exists is True:
        print str(recid), "contains an OSTI ID but no doi"
        no_doi = "%s contains OSTI ID %s but not doi %s<br />"  % (record_link, osti_id, doi)
        return no_doi
    if osti_exists is False and osti_mismatch is False:
        record_add_field(append_record, '001', controlfield_value=str(recid))
        record_add_field(append_record, '035', '', '', subfields=osti_subfields)
        print "%s: added 035__a:%s" % (str(recid), osti_id)
        return print_rec(append_record)


def main():
    input = open('osti-ids-dois.txt', 'r')
    output = open('tmp_osti_ids_dois_append.out', 'w')
    errors = open('tmp_osti_ids_dois_errors.html', 'w')
    done = open('checked-osti-ids.out', 'r+')
    output.write("<collection>")
    paper_list = []
    done_list = []
    recid_counter = 0
    update_counter = 0
    error_counter = 0
    skip_list = [line for line in done.readlines()]
    for line in input.readlines():
        matchObj = re.search(r'(\d+)\t(10.*?)\s|$', line)
        if matchObj:
            if not matchObj.group(1) in skip_list:
                paper_list.append((str(matchObj.group(1)), (matchObj.group(2))))
    print "%s papers to search" % len(paper_list)
    for paper in paper_list:
        if update_counter < 1000:
            search = "0247_a:%s or (035__a:%s 035__9:OSTI)" % (paper[1], paper[0])
            html_search = '<a href="https://inspirehep.net/search?p=%s">%s</a>' % (search, search)
            html_search = re.sub(' ', '+', html_search)
            results = perform_request_search(p=search, cc='HEP')
            if len(results) > 1:
                mismatch = ['<a href="https://inspirehep.net/record/%s">%s</a>' % (str(r), str(r)) for r in results]
                error_counter += 1
                errors.write("Mismatch: %s => %s<br />" % (html_search, ' '.join(mismatch)))
            if len(results) == 1:
                for r in results:
                    recid_counter += 1
                    update = create_xml(recid=r, osti_id=paper[0], doi=paper[1])
                    if update:
                        error_phrases = ("record already contains", "but not doi")
                        if "<record>" in update:
                            update_counter += 1
                            output.write(update)
                            done.write(paper[0]+"\n")
                        if any(x in update for x in error_phrases):
                            error_counter += 1
                            errors.write(update)
    print "%i of %i records updated" % (update_counter, recid_counter)
    print "%i errors" % error_counter
    output.write("</collection>")
    output.close()
    errors.close()
    input.close()
    done.close()
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

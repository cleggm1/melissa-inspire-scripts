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

""" Bibcheck plugin to check emails in 100__m and 700__m of HEP records against 
  HEPNames records and add associated INSPIRE-IDs and ORCIDs to 100__i/j and 700__i/j
  while removing 100__m and 700__m
"""
# 2016-10-24 Haven't added anything that removes emails yet


from invenio.search_engine import perform_request_search, get_fieldvalues
from invenio.bibrecord import print_rec, record_add_field, record_get_field_value
from invenio.bibformat_engine import BibFormatObject
import re

from invenio.bibcheck_task import AmendableRecord
from invenio.bibedit_utils import get_bibrecord

test_records = [1494000, 1493788, 1490920]

def get_id(record, id_type=None):
    """Returns any id with a HEPNames recid"""
    author_id = None
    for item in BibFormatObject(record).fields('035__'):
      if item.has_key('9') and item['9'] == id_type and item.has_key('a'):
        author_id = item['a']
    return author_id

def convert_email_to_id(email):
    """Returns the INSPIRE ID and the ORCID from a search for email in HEPNames"""
    inspire_id = None
    orcid      = None
    emailsearch = '371__m:%s or 371__o:%s or 595__o:%s or 595__m:%s'
    reclist = perform_request_search(p=emailsearch % (email, email, email, email), cc='HepNames')
    if len(reclist) > 1:
      print "More than one HEPNames record contains this email: %s" % email
#      record.warn("More than one HEPNames record contains this email: %s" % email)
    if len(reclist) == 1:
      recid = int(reclist[0])
      print "Found %s in HEPNames record" % email
      if get_id(recid, id_type='INSPIRE'):
        inspire_id = get_id(recid, id_type='INSPIRE')
      if get_id(recid, id_type='ORCID'):
        orcid      = "ORCID:" + get_id(recid, id_type='ORCID')
      return (inspire_id, orcid)


def check_record(record):
    """gets emails from author fields in record and tries to match them with INSPIRE-ID/ORCID from HEPNames"""
    recid = record_get_field_value(record,'001','','','')
    tags = ('100__', '700__')
    subfields = ('m', 'i', 'j')
    fields_dict = {}
    additions = []
    for x, y in [(x,y) for x in tags for y in subfields]:
      for pos, val in record.iterfield(x+y):
          if (x, pos[1]) in fields_dict:
              fields_dict[(x,pos[1])].append((pos, val))
          else:
              fields_dict[(x,pos[1])] = [(pos, val)]
    print fields_dict
    for key in fields_dict:
        inspire_id_true = False
        orcid_true = False
        ids = []
        for item in fields_dict[key]:
            matchObj = re.match('\w{5}(\w)', item[0][0])
            subfield_tag = matchObj.group(1)
            if subfield_tag == 'm':
                email = item[1]
                print 'email:',email
                ids.append((key, convert_email_to_id(email), email))
            if subfield_tag == 'i':
                inspire_id = item[1]
                inspire_id_true = True
                print 'INSPIRE-ID:',inspire_id
            if subfield_tag == 'j':
                if 'ORCID:' in item[1]:
                    orcid = item[1]
                    orcid_true = True
                    print 'ORCID:',orcid
        if ids:
              for id in ids:
                  if id[1][0]:
                      if inspire_id_true:
                        if inspire_id == id[1][0]:
                          print "%s in %s already has an INSPIRE-ID %s" % (id[2], recid, inspire_id)
                        else:
                          print "%s from HEPNames doesn't match id for author %s in record %s (%s)" % (id[1][0], id[2], recid, inspire_id)
#                          record.warn("%s from HEPNames doesn't match id for author %s in record %s (%s)" % (id[1][0], id[2], record, inspire_id))
                      else:
                        print "email: %s, inspire-id: %s" % (id[2], id[1][0])
                        additions.append((id[0], 'i', id[1][0]))
                  if id[1][1]:
                    if orcid_true:
                      if orcid == id[1][1]:
                        print "%s in %s already has an ORICD" % (id[2], recid)
                      else:
                        print "%s from HEPNames doesn't match id for author %s in record %s (%s)" % (id[1][1], id[2], recid, orcid)
#                        record.warn("%s from HEPNames doesn't match id for author %s in record %s (%s)" % (id[1][1], id[2], recid, orcid))
                    else:
                      print "email: %s, orcid: %s" % (id[2], id[1][1])
                      additions.append((id[0], 'j', id[1][1]))
    print "additions: ", additions
    for addition in additions:
        print "Adding %s to tag %s at position %s in %s" % (addition[2], addition[0][0], addition[0][1], recid)
#          record_add_subfield_into(record, addition[0][0], addition[1], addition[2], field_position_local=addition[0][1])

if __name__ == '__main__':
    for r in test_records:
      print 'working on ', r
      record = AmendableRecord(get_bibrecord(r))
      check_record(record)

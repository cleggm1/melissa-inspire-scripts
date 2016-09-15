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

from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field
from invenio.bibformat_engine import BibFormatObject

test_records = [1474920, 1477275, 1474311, 1477281]

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
    reclist = perform_request_search(p = \
        emailsearch % (email, email, email, email), cc='HepNames')
    if len(reclist) > 1:
      print "More than one HEPNames record contains this email: %s" % email
#      record.warn("More than one HEPNames record contains this email: %s" % email)
    if len(reclist) == 1:
      recid = int(reclist[0])
      inspire_id = get_id(recid, id_type='INSPIRE')
      orcid      = "ORCID:" + get_id(recid, id_type='ORCID')
      return (inspire_id, orcid)


def check_record(record):
    """gets emails from author fields in record and tries to match them with INSPIRE-ID/ORCID from HEPNames"""
    tags = ('100__', '700__')
    for tag in tags:
      field_instances = record_get_field_instances(record, tag[0:3], tag[3], tag[4])
    for field_instance in field_instances:
      email_true = False
      inspire_id_true = False
      orcid_true = False
      ids = None
      additions = []
      for code, value in field_instance[0]:
        if code == 'm':
          email = value
          email_true = True
          ids = convert_email_to_id(email)
        if code == 'i':
          inspire_id = value
          inspire_id_true = True
        if code == 'j':
          if 'ORCID:' in value:
            orcid = value
            orcid_true = True
      if ids[0]:
          if inspire_id_true:
            if inspire_id == ids[0]:
              print "%s in %s already has an INSPIRE-ID" % (email, record)
            else:
              print "%s from HEPNames doesn't match id for author %s in record %s (%s)" % (ids[0], email, record, inspire_id)
#              record.warn("%s from HEPNames doesn't match id for author %s in record %s (%s)" % (ids[0], email, record, inspire_id))
          else:
            additions.append(('i', ids[0]))
      if ids[1]:
        if orcid_true:
          if orcid == ids[1]:
            print "%s in %s already has an ORICD" % (email, record)
          else:
            print "%s from HEPNames doesn't match id for author %s in record %s (%s)" % (ids[1], email, recid, orcid)
#            record.warn("%s from HEPNames doesn't match id for author %s in record %s (%s)" % (ids[1], email, recid, orcid))
        else:
          additions.append(('j', ids[1]))
      for addition in additions:
        print "Adding %s to %s in %s" % (addition[1], email, record)
#          record_add_subfield_into(record, tag, addition[0], addition[1], field_position_local=field_instance[0])

if __name__ == '__main__':
    for r in test_records:
      record = get_record(r)
      check_record(record)

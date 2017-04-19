"""
Provides text CV output of papers with current citation counts
"""
#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import print_record

search = raw_input('Search: ')
file = 'IHEP-pub-report.doc'
x = perform_request_search(p=search, cc="HEP")
with open(file, 'w') as output:
    for r in x:
      cv = print_record(r, format='htcv')
      cv = re.sub(r'<br/>', '', cv)
      cv = re.sub(r'\s\s+', '', cv)
      citesearch = perform_request_search(p="refersto:recid:%i" % r, cc="HEP")
      cv = cv + '\n' + str(len(citesearch)) + ' citations'
      print cv + '\n\n'
      output.write(cv +'\n\n')
  

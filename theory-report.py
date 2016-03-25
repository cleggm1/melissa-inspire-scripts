
#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import print_record

date = raw_input('date: ')
file = 'theory_pubs_'+date+'.doc'
output = open(file, 'w')
x = perform_request_search(p="find r fermilab pub t and de %s" % date)
#if False:
    #x = [1416470]
for r in x:
  olivia = print_record(r, format='htcv')
  olivia = re.sub(r'<br/>', '', olivia)
  olivia = re.sub(r'\s\s+', '', olivia)
  reports = get_fieldvalues(r, '037__a')
  pages = get_fieldvalues(r, '300__a')
  print '\n' + olivia
  output.write('\n\n' + olivia +'\n')
  for page in pages:
      print page + ' pp.'
      output.write(page + ' pp.\n')
  for report in reports:
      if re.search(r'FERMILAB', report):
          print report
          output.write(report)
output.close()

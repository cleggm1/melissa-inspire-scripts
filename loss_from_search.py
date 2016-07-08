"""
Runs bibrank on all records in a search
"""

import re
import sys
import datetime
import subprocess
from invenio.search_engine import perform_request_search

VERBOSE = True
VERBOSE = False

search = raw_input("Run bibrank on this search: ")
x = perform_request_search(p=search, cc="HEP")
if len(x) > 0:
    mylist = [str(r) for r in x]
else:
    sys.exit()
    
today = str(datetime.date.today())
newfile = 'tmp_loss_from_search__' + today + '.txt'
output = open(newfile, 'w')
amount = str(len(mylist))
mystring = ','.join(mylist)
mystring2 = 'sudo -u apache /opt/cds-invenio/bin/bibrank -u cleggm1 \
--disable-citation-losses-check -i ' + mystring
if len(mylist) > 1000:
    print "There are %s records that will be touched" % (amount)
    chunks=[mylist[x:x+500] for x in xrange(0, len(mylist), 500)]
    time_inter = 0
    for x in chunks:
        mystring = ','.join(x)
        time_inter += 1
        if time_inter == 0:
            mystring2 = 'sudo -u apache /opt/cds-invenio/bin/bibrank -u cleggm1 \
--disable-citation-losses-check -i ' + mystring
            answer = raw_input("""Execute the following on %s records? y/n

%s

""" % (str(len(x)), mystring2))
            if answer == 'y':
#                print "Testing mode, Bibrank not run"
                subprocess.call(['sudo', '-u', 'apache', '/opt/cds-invenio/bin/bibrank', '-u', 'cleggm1', \
'--disable-citation-losses-check', '-i', mystring])
            else:
                print 'Bibrank not run'
        else:
            time = str(time_inter)+'h'
            mystring2 = 'sudo -u apache /opt/cds-invenio/bin/bibrank -u cleggm1 \
--disable-citation-losses-check -t '+ time+' -i ' + mystring    
            answer = raw_input("""Execute the following on %s records? y/n

%s

""" % (str(len(x)), mystring2))
            if answer == 'y':
#                print "Testing mode, Bibrank not run"
                subprocess.call(['sudo', '-u', 'apache', '/opt/cds-invenio/bin/bibrank', '-u', 'cleggm1', \
'--disable-citation-losses-check', '-t', time, '-i', mystring])
            else:
                print 'Bibrank not run'
else:
    answer = raw_input("""Execute the following on %s records? y/n

%s

""" % (amount, mystring2))

    if answer == 'y':
#        print "Testing mode, Bibrank not run"
        subprocess.call(['sudo', '-u', 'apache', '/opt/cds-invenio/bin/bibrank', '-u', 'cleggm1', \
'--disable-citation-losses-check', '-i', mystring])
        
        output.write(mystring2)
        output.close()
    else:
        print 'Bibrank not run'

"""
Creates an html file of INSPIRE-HEP submissions with ORCID attached
"""

from sys import argv

script, filename = argv
import datetime
import re

#<a href="https://inspirehep.net/record/1202486">1202486</a> <a href="http://orcid.org/0000-0003-4636-8874">0000-0003-4636-8874</a>
today = str(datetime.date.today())
newfile = 'orcid_submissions_' + today + '.html'
input = open(filename, 'r')
output = open(newfile, 'w')
mylist = input.readlines()
newlist = []
for i in mylist:
    matchobj = re.match(r'.*(\d{4}\-\d{4}\-\d{4}\-\d{3}\w).*record/(\d+)', i)
    try:
        orcid = matchobj.group(1)
        recid = matchobj.group(2)
        newitem = '<a href="https://inspirehep.net/record/' + recid + '">' + recid + '</a> <a href="http://orcid.org/' + orcid + '">' + orcid + '</a>'
        newlist.append(newitem)
        print orcid, recid, newitem
    except:
        print i
#recid = [i.split('https://inspirehep.net/record/')[-1].rsplit('/export/hm')[0] for i in mylist]
#orcid = [i.split('http://orcid.org/')[-1] for i in mylist]
#mylist = [i.split('https://inspirehep.net/record')[-1] for i in mylist]
#mylist = [i.split('https://inspirehep.net/')[-1] for i in mylist]
#mylist = [i.replace(r'/export/hm  http://orcid.org/', ' orcid: ').replace(r'/', 'recid: ') for i in mylist]
print newlist
mystring = '<br /> '.join(newlist)
output.write(mystring)
output.close()

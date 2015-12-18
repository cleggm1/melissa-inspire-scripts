import re
import datetime
import subprocess
#from sys import argv

#script, filename = argv

VERBOSE = True
VERBOSE = False
mylist = []

for i in open('tmp_citationloss.in.txt','r').readlines() :
    recid = 0
    matchObj = re.search(r"Record (\d+) lost too many", i)
    if matchObj:
        recid = matchObj.group()
        recid = re.sub(r'\D', r'', recid)
        mylist.append(recid)


today = str(datetime.date.today())
newfile = 'tmp_citationloss_' + today + '.txt'
#input = open(filename, 'r')
output = open(newfile, 'w')
#mylist = input.readlines()
#deletes first line
#del mylist[0]
#mylist = [i.split(' lost')[0] for i in mylist]
#mylist = [i.split('Record ')[-1] for i in mylist]
mystring = ','.join(mylist)
mystring2 = 'sudo -u apache /opt/cds-invenio/bin/bibrank -u cleggm1 --disable-citation-losses-check -i ' + mystring

answer = raw_input("""Execute the following? y/n

%s

""" % mystring2)

if answer == 'y':
    subprocess.call(['sudo', '-u', 'apache', '/opt/cds-invenio/bin/bibrank', '-u', 'cleggm1', '--disable-citation-losses-check', '-i',$
    output.write(mystring2)
    output.close()
else:
    print 'Bibrank not run'



from invenio.bibrecord import print_rec, record_add_field
from invenio.search_engine import perform_request_search
import re
import datetime
import os

VERBOSE = True
VERBOSE = False

today = str(datetime.date.today())
i = 0
while os.path.exists('/nashome/c/cleggm1/tmp_jobhidden_' + t
oday + '_%s_correct.txt' % i):
    i += 1
newfile = '/nashome/c/cleggm1/tmp_jobhidden_' + today + '_%s
_correct.txt' % i

output = open(newfile, 'w')


for i in open('tmp_jobhidden.in','r').readlines() :
    recid = 0
    matchObj = re.search(r"Remove posting in HEPJobs (\d+)", i)
#    print i
    if matchObj:
        #if VERBOSE:
            #print 'VERBOSE', match.Obj.group()
        recid = matchObj.group()
        recid = re.sub(r'\D', r'', recid)
    else:
        matchObj = re.search(r"Remove\-listing\-(JOBSUBMIT\-JOB\-\S+)", i)
        if matchObj:
            #if VERBOSE:
                #print 'VERBOSE', matchObj.group()
            submission_id = matchObj.group(1)
            search = '037__a:' + submission_id
            if VERBOSE:
                print 'VERBOSE', search
            result = perform_request_search(p = search, cc = "Jobs")
            if len(result) == 1:
                recid = result[0]
    if recid:
        common_fields = {}
        common_tags = {}
        #    print i
    if matchObj:
        #if VERBOSE:
            #print 'VERBOSE', match.Obj.group()
        recid = matchObj.group()
        recid = re.sub(r'\D', r'', recid)
    else:
        matchObj = re.search(r"Remove\-listing\-(JOBSUBMIT\-JOB\-\S+)", i)
        if matchObj:
            #if VERBOSE:
                #print 'VERBOSE', matchObj.group()
            submission_id = matchObj.group(1)
            search = '037__a:' + submission_id
            if VERBOSE:
                print 'VERBOSE', search
            result = perform_request_search(p = search, cc = "Jobs")
            if len(result) == 1:
                recid = result[0]
    if recid:
        common_fields = {}
        common_tags = {}
        record_add_field(common_fields, '001', controlfield_value=str(recid))
        common_tags['980__'] = [('a', 'JOBHIDDEN')]
        for key in common_tags:
            tag = key
            record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
        #print print_rec(common_fields)
        output.write(print_rec(common_fields))

output.close()


search_str = 'JOBHIDDEN'
count = 0
read_file = open(newfile, 'r')

for line in read_file:
    if search_str in line:
        count += 1

print count, 'jobs will be removed'
print newfile
read_file.close()

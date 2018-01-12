#Extracts all email addresses with a particular string and their associated ORCID'
from invenio.search_engine import perform_request_search, get_fieldvalues
from invenio.bibformat_engine import BibFormatObject

rawemail = r'/@fnal\.gov/'
emailsearch = '371__m:%s or 371__o:%s or 595__o:%s or 595__m:%s) and 035:ORCID' % (rawemail,rawemail,rawemail,rawemail)
emailstring = '@fnal.gov'
counter = 0
with open('fermi-orcids.csv', 'w') as output:
    results = perform_request_search(p=emailsearch, cc='HepNames')
    for r in results:
        for item in BibFormatObject(r).fields('035__'):
            if item.has_key('9') and item['9'] == 'ORCID' and item.has_key('a'):
                orcid = item['a']
        emails = []
        tags = ['371__o', '371__m', '595__o', '595__m']
        for tag in tags:
            emails.append(get_fieldvalues(r, tag))
        emails = [x for y in emails for x in y]
        for x in emails:
            if emailstring in x:
                email = x
        if email and orcid:
            output.write('%s,%s\n'% (email, orcid))
            print email, orcid
            counter+=1
print counter


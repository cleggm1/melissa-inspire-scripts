import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues

issues = []
output = open('needs_issues_added.html', 'w')
search = "fin j Electron.J.Theor.Phys."
x = perform_request_search(p=search, cc="HEP")
for r in x:
    volume = get_fieldvalues(r, "773__v")
    for i in volume:
        v = i
    year = get_fieldvalues(r, "773__y")
    for i in year:
        y = i
    pages = get_fieldvalues(r, "773__c")
    for i in pages:
        c = i
        shortpage = c
        matchObj = re.search(r'(\d+)-\d+', c)
        if matchObj:
            shortpage = matchObj.group(1)
    issue = get_fieldvalues(r, "773__n")
    link = '<a href="https://inspirehep.net/record/%d">Electron.J.Theor.Phys. %s (%s) %s</a><br />' % (r, v, y, c)
    refsearch = '999C5s:"Electron.J.Theor.Phys.,%s,%s*"' % (v, shortpage)
    w =  perform_request_search(p=refsearch, cc="HEP")
    if len(w) > 0:
        reflink = '&nbsp;&nbsp;&nbsp;&nbsp;<a href=\'https://inspirehep.net/search?p=999C5s:"Electron.J.Theor.Phys.,%s,%s*"&of=hb\'>999C5s:"Electron.J.Theor.Phys.,%s,%s*"</a><br />' % (v, shortpage, v, shortpage)
        link = link+reflink
    if issue:
        issues.append(r)
    else:
        output.write(link)
output.close()
print "%d of %d records already having an issue" % (len(issues), len(x))

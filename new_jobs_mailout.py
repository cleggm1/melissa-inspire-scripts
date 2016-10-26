import datetime
import re
from invenio.search_engine import perform_request_search, print_record

from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_jobs_mail(content):
    html= """<html>
<head></head>
<body>
<p><center>INSPIRE HEPJobs listing of new jobs</p>
<p><a href="http://inspirehep.net/search?cc=Jobs">http://inspirehep.net/search?cc=Jobs</a></center></p>
<p>Want to see job postings sorted by deadline? Just append "&sf=046__i&so=d" to any search, e.g.<a href="https://inspirehep.net/search?cc=Jobs&sf=046__i&so=d">https://inspirehep.net/search?cc=Jobs&sf=046__i&so=d</a>.</p>
<p>
%s
</p>
<p>Follow INSPIRE on <a href="http://twitter.com/inspirehep">Twitter</a>.</p>
<p>*********************************************************<br />
To unsubscribe from this list do NOT reply to this email.<br />
Instead send email to <a href="mailto:listserv@fnal.gov">listserv@fnal.gov</a>.
In the body of the e-mail type:<br />
&nbsp;&nbsp;&nbsp;&nbsp;signoff jobs<br />
Do not include any other text or type anything in the subject line.<br />
*********************************************************</p>
<p>The INSPIRE HEPJobs database is administered by the Fermilab Library.<br />
Please send any comments or questions to <a href="mailto:jobs@inspirehep.net">jobs@inspirehep.net</a>.</p>
""" % content
    print html
    text = BeautifulSoup(html).text

    hepjobs_email = '"HEPJobs Database Administrator" <jobs@inspirehep.net>'

    # Create message container - the correct MIME type is
    # multipart/alternative.

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'INSPIRE HEPJobs listing'
    msg['From'] = hepjobs_email
    msg['To'] = hepjobs_email
#    msg['BCC'] = 'jobs@fnal.gov'
    msg['BCC'] = 'cleggm1@fnal.gov'
    msg['X-Auto-Response-Suppress'] = 'OOF, DR, RN, NRN'

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message,
    # in this case the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    stmp_email = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    stmp_email.sendmail(hepjobs_email, hepjobs_email, msg.as_string())
    stmp_email.quit()

def main():
    content = []
    recids = []
    date_last_run = False
    latest_recid = False
    latest = False
    filename = re.sub(".py", "_log", "tmp_"+__file__)
    stored_file = open(filename, 'r+')
    for line in stored_file.readlines():
        matchObj1 = re.match('most recent recid = (\d+)', line)
        if matchObj1:
            latest_recid = matchObj1.group(0)
        matchObj2 = re.match('date last run = (.*)', line)
        if matchObj2:
            date_last_run = matchObj2.group(0)
    if date_last_run and latest_recid:
        results = perform_request_search(p="fin da >= %s" % date_last_run, cc="Jobs")
    else:
        date_last_run = raw_input("""Couldn't find the date of the most recently sent New Jobs Mailout.
Send jobs posted on and after this date (yyyy-mm-dd): """)
        if date_last_run:
            results = perform_request_search(p="fin da >= %s" % date_last_run, cc="Jobs")
    if len(results) > 0:
        for r in results:
            recids.append(r)
        print recids
        if latest_recid:
            recids = [x for x in recids if x > latest_recid]
        print recids
        if recids:
            latest = max(recids)
        else:
            print "No postings since %s." % date_last_run

    else:
        print "No postings since %s." % date_last_run
    if latest:
        stored_file.write("most recent recid = %s" % str(latest))
        today = str(datetime.date.today())
        stored_file.write("date last run = %s" % today)
        stored_file.write("records in last mailout = %s" % ', '.join(str(x) for x in sorted(recids)))
        for r in recids:
            content.append(print_record(r,ot=[],format='he'))
        content = ''.join(content)
        send_jobs_mail(content)
    stored_file.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

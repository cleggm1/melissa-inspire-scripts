# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_jobs_mail():
    try_send = True
    content = ""
    while try_send:
        print "Paste records to include in the mailout (he format). Type 'done' on a blank line when finished: "
        stopword = False
        while not stopword:
            line = raw_input()
            if line.strip().lower() == 'done':
                stopword = True
            else:
                matchObj = re.match(r"^(\d{4}\-\d{2}\-\d{2}:).*?(\[Deadline:.*?\])", line)
                if matchObj:
                    added = matchObj.group(1)
                    bold_added = "<b>"+added+"</b>"
                    deadline = matchObj.group(2)
                    bold_deadline = "<b>"+deadline+"</b>"
                    line = line.replace(added, bold_added).replace(deadline, bold_deadline)
                content += "%s<br />\n" % line
        html= """<html>
<head></head>
<body>
<p>INSPIRE HEPJobs listing of new jobs<br />
<a href="http://inspirehep.net/search?cc=Jobs">http://inspirehep.net/search?cc=Jobs</a><p/>
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
        text = BeautifulSoup(html).text
        print "\n\n\n"+text+"\n\n\n"
        send = raw_input("Mailout OK to send? (y/n): ")
        if send == 'y':
            hepjobs_email = '"HEPJobs Database Administrator" <jobs@inspirehep.net>'
#            bcc = 'jobs@fnal.gov,hoc@fnal.gov'
            bcc = 'cleggm1@fnal.gov,hoc@fnal.gov'

            # Create message container - the correct MIME type is
            # multipart/alternative.
            rcpt = bcc.split(",")+[hepjobs_email]
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'INSPIRE HEPJobs listing'
            msg['From'] = hepjobs_email
            msg['To'] = hepjobs_email
            msg['Bcc'] = bcc
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
            stmp_email.sendmail(hepjobs_email, rcpt, msg.as_string())
            stmp_email.quit()
            print "Message sent!"
            try_send = False
        elif send == 'n':
            print "Message not sent."

if __name__ == '__main__':
    try:
        send_jobs_mail()
    except KeyboardInterrupt:
        print 'Exiting'

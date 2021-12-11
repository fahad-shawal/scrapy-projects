import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from html_template import html_t

FROM_EMAIL = 'notificationpinnacle@gmail.com'
TO_EMAILS = 'fahadshawal@gmail.com'
SUBJECT = 'Sending with Twilio SendGrid is Fun'
HTML_CONTENT = html_t


message = Mail(
    from_email=FROM_EMAIL,
    to_emails=TO_EMAILS,
    subject=SUBJECT,
    html_content=HTML_CONTENT)
try:
    sg = SendGridAPIClient('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')
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)
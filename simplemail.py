# A simple e-mail wrapper
import smtplib
from email.mime.text import MIMEText


def create_server(netid=None, password=None):
    s = smtplib.SMTP()
    s.connect('smtp.duke.edu', 587)
    # Start TLS
    s.ehlo()
    s.starttls()
    s.ehlo()
    # Get user info if it wasn't provided
    if not netid:
        netid = input('NetID: ')
    if not password:
        password = input('Password: ')
    # Next, log in to the server
    s.login(netid, password)
    return (s, netid)

def send_email(server, send_to, send_from, subject, message):
    if not isinstance(send_to, list):
        send_to = [send_to]
    try:
        server.sendmail(send_from, send_to, message.as_string())
    except Exception,R:
        print R

def close_server(s):
    s.quit()

if __name__ == "__main__":
    (server, netid) = create_server()
    to = input('Recipient: ')
    sub = input('Subject: ')
    msg = input('Message: ')
    me = '%s@duke.edu' % (netid)
    send_email(server, to, me, sub, msg)
    close_server(s)

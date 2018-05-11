import imaplib
from config import emConfig
import smtplib
from email.message import EmailMessage
import re
from emapp import emrdb
from emapp.models import Service
import email
from emapp.tokenizer import tknzr, tkformat
from emapp.storage import storedata
from bs4 import BeautifulSoup
from dateutil import parser
from dateutil.tz import gettz

'''
s = readstatus()
    frmss = StartStop()
    if s.running:
        livethreads = threading.enumerate()
        mnthr = None
        for lvth in livethreads:
            if lvth.name == "maint":
                mnthr = lvth
                break
            if mnthr is None:
                maint(1)
'''


def email_address(string):
    # Regular expression matching according to RFC 2822 (http://tools.ietf.org/html/rfc2822)
    rfc2822_re = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    email_prog = re.compile(rfc2822_re, re.IGNORECASE)
    eml = email_prog.findall(string)
    if len(eml) == 0:
        return None
    else:
        return eml


def readstatus():
    try:
        s = Service.query.one()
    except:
        s = Service(running=0)
        emrdb.session.add(s)
        emrdb.session.commit()
    return s


def store_email(emailid, conn, folder):
    folder = folder.upper()
    try:
        r, d = conn.select(folder)
        if r == 'NO':
            r, d = conn.create(folder)
        r, d = conn.select('INBOX')
    except AttributeError:
        print(r, " - ", d)
    conn.store(emailid, '-FLAGS', '\\Seen')
    conn.store(emailid, '+X-GM-LABELS', folder)
    conn.store(emailid, '+FLAGS', '\\Deleted')  # Borra el de INBOX
    # mov, data = conn.uid('STORE', emailid, '+FLAGS', '(\Deleted)')  # Mantiene las 2 copias
    conn.expunge()


def mainprocess():
    imapserver = emConfig.IMAP
    con = auth(imapserver)
    r, d = con.select('INBOX')
    if r != 'OK':
        con.logout()
        return True
    tzinfos = {"CST": gettz("America/Mexico_City")}
    # for i in range(int(b'1'), int(d[0]) + 1):
    # for i in range(int(b'1'), int(d[0]) + 1):
    i = 0
    while int(d[0]) >= 1:
        # idmail = str(i).encode('ascii')
        idmail = str(1).encode('ascii')
        result, data = con.fetch(idmail, '(RFC822)')
        if result == 'OK':
            raw = email.message_from_bytes(data[0][1])
            soup = BeautifulSoup(get_body(raw), 'html.parser')
            whereat = raw['From'].find("@", 0) + 1
            wheredot = raw['From'].find(".", whereat)
            cliente = raw['From'][whereat:wheredot]
            frmt = tkformat(soup.get_text())
            if frmt == 1:
                i += 1
                emldta = (email_address(raw['To']),
                            email_address(raw['From']),
                            raw['Subject'].replace('***SPAM***', '').strip(),
                            parser.parse(raw['Date'].replace("CST_NA", "CST"), tzinfos=tzinfos).strftime('%d-%m-%Y %H:%M:%S'),
                            cliente,
                            raw['Message-ID'])
                tokens = tknzr(soup.get_text())
                try:
                    tokens[1] = parser.parse(tokens[1].replace("CST_NA", "CST"), tzinfos=tzinfos).strftime('%d-%m-%Y %H:%M:%S')
                except:
                    None
                try:
                    tokens[2] = parser.parse(tokens[2].replace("CST_NA", "CST"), tzinfos=tzinfos).strftime('%d-%m-%Y %H:%M:%S')
                except:
                    None
                storedata(emldta, tokens)
            store_email(idmail, con, cliente)
            r, d = con.select('INBOX')
        else:
            fin(con)
            return True
        print(str(i) + "/" + str(int(d[0]) + 1) + " - " + cliente + " - ")
    fin(con)


def get_body(msg):  # extracts the body from the email
    if msg.is_multipart():
        return get_body(msg.get_payload(1))
    else:
        return msg.get_payload(None, True)


def auth(conf):  # sets up the auth
    conn = imaplib.IMAP4_SSL(conf['server'], conf['port'])
    conn.login(conf['user'], conf['password'])
    return conn


def fin(cnn):  # closes the folder and terminates the connection
    cnn.close()
    cnn.logout()

'''
def send_async_email(app, srv, msge):
    with app.app_context():
        if not srv['SSL']:
            smtp = smtplib.SMTP(srv['server'], srv['port'])
            smtp.starttls()
        else:
            smtp = smtplib.SMTP_SSL(srv['server'], srv['port'])  # Use this for Nemaris Server
        smtp.login(srv['user'], srv['password'])
        smtp.sendmail(msge['From'], msge['To'], msge.as_string())
        smtp.quit()


def send_email(server, msg):
    threading.Thread(target=send_async_email, args=(app, server, msg)).start()


def send_password_reset_email(usr):
    smtpserver = app.config['SMTP']

    msg = EmailMessage()
    msg['Subject'] = "Restablecer Password - Robot Email"
    msg['From'] = smtpserver['user']
    msg['To'] = usr.email
    msg.set_type('text/html')

    token = usr.get_reset_password_token()
    msg.set_content(render_template('email/reset_password.txt', user=usr, token=token))
    html_msg = render_template('email/reset_password.html', user=usr, token=token)
    msg.add_alternative(html_msg, subtype="html")

    send_email(smtpserver, msg)
'''
import imaplib
from config import emConfig
import smtplib
from email.message import EmailMessage
import re
from emapp import emrdb
import email
from emapp.tokenizer import tknzr, tkformat
from emapp.storage import storedata
from bs4 import BeautifulSoup
from dateutil import parser
from dateutil.tz import gettz


def email_address(string):
    # Regular expression matching according to RFC 2822 (http://tools.ietf.org/html/rfc2822)
    rfc2822_re = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    email_prog = re.compile(rfc2822_re, re.IGNORECASE)
    eml = email_prog.findall(string)
    if len(eml) == 0:
        return None
    else:
        return eml


def store_email(emailid, conn, folder):
    # conn.delete('INBOX.TEST')
    # folder = 'INBOX.' + folder.upper()
    folder = folder.upper()
    try:
        r, d = conn.select(folder)
        if r == 'NO':
            if str.find(str(d[0]), 'prefixed with') == -1:
                r, d = conn.create(folder)
            else:
                folder = 'INBOX.' + folder.upper()
                store_email(emailid, conn, folder)
                return True
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
    i = 0
    while int(d[0]) >= 1:
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

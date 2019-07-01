import imaplib
from config import EmConfig
from datetime import datetime
import re
import email
from emapp.tokenizer import tknzr, tkformat
from emapp.storage import storedata, igualar_tablas, lista_clientes
from emapp import logger
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


def store_email(emailid, conn, folder, is_un):
    # conn.delete('INBOX.TEST')
    topfolder = 'INBOX/CLIENTES'
    folder = 'INBOX/CLIENTES/' + folder.upper()
    try:
        r, d = conn.select(topfolder)
        if r == 'NO':
            r, d = conn.create(topfolder)
            if r != "OK":
                logger.error('No fue posible crear el folder CLIENTES')
                raise SystemExit(0)
            else:
                conn.subscribe(topfolder)
        r, d = conn.select(folder)
        if r == 'NO':
            r, d = conn.create(folder)
            if r != "OK":
                logger.error('No fue posible crear el folder {}'.format(folder))
                raise SystemExit(0)
            else:
                conn.subscribe(folder)
        conn.select('INBOX')
    except AttributeError:
        logger.warning('No se pudo seleccionar/crear la carpeta: {} en el SMTP'.format(folder))
        logger.error('Error: {}'.format(AttributeError))
        raise SystemExit(0)
    try:
        ''' gmail
        conn.store(emailid, '-FLAGS', '\\Seen')
        conn.store(emailid, '+X-GM-LABELS', folder)
        conn.store(emailid, '+FLAGS', '\\Deleted')  # Borra el de INBOX
        # mov, data = conn.uid('STORE', emailid, '+FLAGS', '(\Deleted)')  # Mantiene las 2 copias
        '''
        resp, data = conn.fetch(emailid, "(UID)")
        msg_uid = str(data[0])[str(data[0]).find('UID') + 4: str(data[0]).find(')')]
        if is_un:
            conn.uid('STORE', msg_uid, '-FLAGS', '(\Seen)')
        result = conn.uid('COPY', msg_uid, folder)
        if result[0] == 'OK':
            conn.uid('STORE', msg_uid, '+FLAGS', '(\Deleted)')
            conn.expunge()
        else:
            logger.error('No se pudo guardar el correo en la carpeta: {}'.format(folder))
            raise SystemExit(0)
    except:
        fin(conn)
        logger.error('No se pudo guardar el correo en la carpeta: {}'.format(folder))
        raise SystemExit(0)


def del_oldmail(conn, explicit):
    clis = lista_clientes()
    topfolder = 'INBOX/CLIENTES'
    tzinfos = {"CST": gettz("America/Mexico_City")}
    try:
        r, d = conn.select(topfolder)
        if r == 'NO':
            return True
    except AttributeError:
        logger.warning('Error al seleccionar la carpeta: {} en el SMTP'.format(topfolder))
        logger.error('Error: {}'.format(AttributeError))
        raise SystemExit(0)
    for cs in clis:
        folder = 'INBOX/CLIENTES/' + clis[cs]
        if explicit:
            print('Revisando mails viejos de: ', folder)
        try:
            r, d = conn.select(folder)
            if r == 'OK':
                cont = True
            else:
                cont = False
        except AttributeError:
            logger.warning('Error al seleccionar la carpeta: {} en el SMTP'.format(folder))
            logger.error('Error: {}'.format(AttributeError))
            raise SystemExit(0)
        while cont:
            if int(d[0]) >= 1:
                idmail = str(1).encode('ascii')
                result, data = conn.fetch(idmail, '(RFC822)')
                if result == 'OK':
                    raw = email.message_from_bytes(data[0][1])
                    fecha = parser.parse(raw['Date'].replace("CST_NA", "CST"), tzinfos=tzinfos).strftime(
                        '%d-%m-%Y %H:%M:%S')
                    fechamail = datetime.strptime(fecha, '%d-%m-%Y %H:%M:%S')
                    now = datetime.now()
                    lapso = (now - fechamail)
                    dias = lapso.days + (lapso.seconds / 86400) + (lapso.microseconds / 86400000000.00056)
                    if explicit:
                        print('\tBorrando mail No. ', d[0], ' / Razon, edad: ', dias, 'dias')
                    if dias > 7:
                        try:
                            resp, dt = conn.fetch(idmail, "(UID)")
                            msg_uid = str(dt[0])[str(dt[0]).find('UID') + 4: str(dt[0]).find(')')]
                            conn.uid('STORE', msg_uid, '+FLAGS', '(\Deleted)')
                            conn.expunge()
                        except AttributeError:
                            logger.warning('No se pudo eliminar el correo de la carpeta: {} en el SMTP'.format(folder))
                            logger.error('Error: {}'.format(AttributeError))
                            raise SystemExit(0)
                    else:
                        cont = False
                    r, d = conn.select(folder)
                else:
                    fin(conn)
                    logger.error('No se pudo leer el ultimo correo de {}'.format(folder))
                    raise SystemExit(0)
            else:
                cont = False


def mainprocess(explicit):
    if explicit:
        print('Iniciando Proceso principal')
    while True:
        tablaslistas = igualar_tablas()
        if tablaslistas == 'OK':
            if explicit:
                print('Tablas listas')
            break
    imapserver = EmConfig.IMAP
    try:
        con = auth(imapserver)
        if explicit:
            print('Conectado a server de mail')
    except:
        logger.error('No se pudo conectar a la cuenta de correo: {}'.format(imapserver['user']))
        raise SystemExit(0)
    del_oldmail(con, explicit)
    r, d = con.select('INBOX')
    if r != 'OK':
        con.logout()
        logger.error('No se pudo seleccionar INBOX de: {}'.format(imapserver['user']))
        raise SystemExit(0)
    else:
        if explicit:
            print('INBOX seleccionado')
    tzinfos = {"CST": gettz("America/Mexico_City")}
    i = 0
    while int(d[0]) >= 1:
        idmail = str(1).encode('ascii')
        unread = con.search(None, '(UNSEEN)')
        if unread[0] == 'OK':
            is_unread = idmail in unread[1][0]
        else:
            is_unread = False
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
                          parser.parse(raw['Date'].replace("CST_NA", "CST"), tzinfos=tzinfos).strftime(
                              '%d-%m-%Y %H:%M:%S'),
                          cliente,
                          raw['Message-ID'])
                tokens = tknzr(soup.get_text())
                try:
                    tokens[1] = datetime.strptime(tokens[1].replace(" CST_NA", "").replace(" CST", ""),'%d.%m.%Y %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
                except:
                    logger.warning(
                        'No se pudo hacer el parse de: {} | Message-ID: {}'.format(tokens[1], raw['Message-ID']))
                    tokens[1] = datetime.strptime('01-01-1901 0:01:00', '%d-%m-%Y %H:%M:%S')
                try:
                    tokens[2] = datetime.strptime(tokens[2].replace(" CST_NA", "").replace(" CST", ""),'%d.%m.%Y %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
                except:
                    logger.warning(
                        'No se pudo hacer el parse de: {} | Message-ID: {}'.format(tokens[2], raw['Message-ID']))
                    tokens[2] = datetime.strptime('01-01-1901 0:01:00', '%d-%m-%Y %H:%M:%S')
                storedata(emldta, tokens)
            store_email(idmail, con, cliente, is_unread)
            r, d = con.select('INBOX')
        else:
            fin(con)
            logger.error('No se pudo leer el primer correo de INBOX de {}'.format(imapserver['user']))
            raise SystemExit(0)
        if explicit:
            print(str(i) + "/" + str(int(d[0]) + 1) + " - " + cliente + " - ")
    fin(con)
    logger.info('Email Robot finalizó: {} correos procesados'.format(i))


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

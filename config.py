import vars
import cx_Oracle
# import os
# basedir = os.path.abspath(os.path.dirname(__file__))


def buildconnstring():
    DBCRED = {'dburl': vars.DB_URL or 'URL-de-la-base',
              'dbport': vars.DB_PORT or 'PUERTO-de-la-base',
              'dbservice': vars.DB_SERVICE or 'SERVICENAME-de-la-base',
              'dbuser': vars.DB_USER or 'USER-de-la-base',
              'dbpass': vars.DB_PASS or 'PASS-de-la-base'}
    dnsStr = cx_Oracle.makedsn(DBCRED['dburl'], DBCRED['dbport'], DBCRED['dbservice'])
    dnsStr = dnsStr.replace('SID', 'SERVICE_NAME')
    connect_str = 'oracle://' + DBCRED['dbuser'] + ':' + DBCRED['dbpass'] + '@' + dnsStr
    return connect_str


class EmConfig(object):
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'emapp.db'
    SQLALCHEMY_DATABASE_URI = buildconnstring()
    SMTP = {'user': vars.SMTP_USER or 'Usuario-de-SMTP',
            'password': vars.SMTP_PASS or 'Password-de-SMTP',
            'server': vars.SMTP_SRV or 'Servidor-de-SMTP',
            'port': vars.SMTP_PORT or 'Puerto-de-SMTP',
            'SSL': vars.SMTP_SSL or 'SSL-de-SMTP'}
    IMAP = {'user': vars.IMAP_USER or 'Usuario-de-IMAP',
            'password': vars.IMAP_PASS or 'Password-de-IMAP',
            'server': vars.IMAP_SRV or 'Servidor-de-IMAP',
            'port': vars.IMAP_PORT or 'Puerto-de-IMAP'}




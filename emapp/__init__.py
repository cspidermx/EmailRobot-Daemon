import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import emConfig


logger = logging.getLogger('EmailRobot')
if emConfig.SMTP['user'] != 'Usuario-de-SMTP':
    auth = (emConfig.SMTP['user'], emConfig.SMTP['password'])
    mail_handler = SMTPHandler(
                mailhost=(emConfig.SMTP['server'], emConfig.SMTP['port']),
                fromaddr='no-reply@' + emConfig.SMTP['server'],
                toaddrs='carlos.barajas@nemaris.com.mx', subject='Falla en robot de Email',
                credentials=auth, secure=emConfig.SMTP['SSL'])
    mail_handler.setLevel(logging.ERROR)
    logger.addHandler(mail_handler)
if not os.path.exists('logs'):
        os.mkdir('logs')
file_handler = RotatingFileHandler('logs/emailrobot.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.info('Email Robot iniciado')

try:
    engine = create_engine(emConfig.SQLALCHEMY_DATABASE_URI)
    Base = declarative_base()
    Base.metadata.bind = engine
    emrdb = sessionmaker(bind=engine)
    emrdbs = emrdb()
except:
    logger.error('No se pudo inicializar la Base de Datos: {}'.format(emConfig.SQLALCHEMY_DATABASE_URI))
    raise SystemExit(0)


from emapp import models, emailfunc


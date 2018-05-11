import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from config import emConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config.from_object(emConfig)
emrdb = SQLAlchemy(app)
migratedb = Migrate(app, emrdb)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
auth = (app.config['SMTP']['user'], app.config['SMTP']['password'])
mail_handler = SMTPHandler(
            mailhost=(app.config['SMTP']['server'], app.config['SMTP']['port']),
            fromaddr='no-reply@' + app.config['SMTP']['server'],
            toaddrs='carlos.barajas@nemaris.com.mx', subject='Fall en robot SAP',
            credentials=auth, secure=app.config['SMTP']['SSL'])
mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)
if not os.path.exists('logs'):
        os.mkdir('logs')
file_handler = RotatingFileHandler('logs/emailrobot.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Email Robot iniciado')


from emapp import routes, models, emailfunc, errors


emailfunc.maint(1)

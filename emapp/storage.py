from emapp.models import Email, EmailFrom, EmailTo, Alerta
from emapp import emrdbs, logger
from datetime import datetime
from sqlalchemy.sql.expression import func


def storedata(emldta, tokens):
    qryemlid = emrdbs.query(func.max(Email.id)).one()
    if qryemlid[0] is not None:
        emlid = qryemlid[0] + 1
    else:
        emlid = 1
    fch = datetime.strptime(emldta[3], '%d-%m-%Y %H:%M:%S')
    twin = emrdbs.query(Email.id).filter_by(asunto=emldta[2], fecha=fch, cliente=emldta[4], idmsg=emldta[5])
    if twin.count() == 0:
        eml = Email(id=emlid, asunto=emldta[2], fecha=fch, cliente=emldta[4], idmsg=emldta[5])
        emrdbs.add(eml)
    else:
        logger.warning('Email ya se encuentra en la base de datos')
    for emladdr in emldta[0]:
        twin = emrdbs.query(EmailTo.id).filter_by(id=emlid, to_=emladdr)
        if twin.count() == 0:
            emlto = EmailTo(id=emlid, to_=emladdr)
            emrdbs.add(emlto)
        else:
            logger.warning('Email-To repetido en la base de datos')
    for emladdr in emldta[1]:
        twin = emrdbs.query(EmailFrom.id).filter_by(id=emlid, frm=emladdr)
        if twin.count() == 0:
            emlfrom = EmailFrom(id=emlid, frm=emladdr)
            emrdbs.add(emlfrom)
        else:
            logger.warning('Email-From repetido en la base de datos')
    try:
        sdt = datetime.strptime(tokens[1], '%d-%m-%Y %H:%M:%S')
    except:
        sdt = datetime.strptime('01-01-1901 0:01:00', '%d-%m-%Y %H:%M:%S')
    try:
        edt = datetime.strptime(tokens[2], '%d-%m-%Y %H:%M:%S')
    except:
        edt = datetime.strptime('01-01-1901 0:01:00', '%d-%m-%Y %H:%M:%S')
    twin = emrdbs.query(Alerta.id).filter_by(alert_details=tokens[0], start_datetime=sdt, end_datetime=edt,
                                             managed_object=tokens[3], category_=tokens[4], rating=tokens[5],
                                             status=tokens[6], description=tokens[7], analysis_tools=tokens[8])
    if twin.count() == 0:
        alert = Alerta(id=emlid, alert_details=tokens[0], start_datetime=sdt, end_datetime=edt, managed_object=tokens[3],
                       category_=tokens[4], rating=tokens[5], status=tokens[6], description=tokens[7],
                       analysis_tools=tokens[8])
        emrdbs.add(alert)
    else:
        logger.warning('Alerta ya se encuentra en la base de datos')
    emrdbs.commit()

from emapp.models import Email, EmailFrom, EmailTo, Alerta
from emapp import emrdbs, logger
from datetime import datetime
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import DatabaseError


def lista_clientes():
    cliuniq = {'cliente1': 'SAP'}
    qryclis = emrdbs.query(Email.cliente).distinct().all()
    if len(qryclis) > 0:
        i = 1
        for cli in qryclis:
            for r in cli:
                i += 1
                cliuniq['cliente' + str(i)] = r.upper()
    return cliuniq


def igualar_tablas():
    try:
        qryemlid = emrdbs.query(func.max(Email.id)).one()
    except DatabaseError as dberr:
        logger.warning('Error de la base de datos: {}'.format(dberr.code))
        logger.error('Error: {}'.format(dberr.orig.args[0].message))
        raise SystemExit(0)
    if qryemlid[0] is not None:
        emlid = qryemlid[0]
    else:
        emlid = 0
    qryemltoid = emrdbs.query(func.max(EmailTo.id)).one()
    if qryemltoid[0] is not None:
        emltoid = qryemltoid[0]
    else:
        emltoid = 0
    qryemlfrid = emrdbs.query(func.max(EmailFrom.id)).one()
    if qryemlfrid[0] is not None:
        emlfrid = qryemlfrid[0]
    else:
        emlfrid = 0
    qryalertid = emrdbs.query(func.max(Alerta.id)).one()
    if qryalertid[0] is not None:
        alertid = qryalertid[0]
    else:
        alertid = 0
    if not (emlid == emltoid == emlfrid == alertid):
        l_id = [emlid, emltoid, emlfrid, alertid]
        last = min(l_id)
        if emlid > last:
            emrdbs.query(Email).filter_by(id=emlid).delete()
        if emltoid > last:
            emrdbs.query(EmailTo).filter_by(id=emltoid).delete()
        if emlfrid > last:
            emrdbs.query(EmailFrom).filter_by(id=emlfrid).delete()
        if alertid > last:
            emrdbs.query(Alerta).filter_by(id=alertid).delete()
        emrdbs.commit()
        return 'DEL'
    else:
        return 'OK'


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
        logger.warning('Email repetido en la base de datos: Email de {} el {}'.format(emldta[4], fch.strftime(
            '%d-%m-%Y %H:%M:%S')))
    for emladdr in emldta[0]:
        twin = emrdbs.query(EmailTo.id).filter_by(id=emlid, to_=emladdr)
        if twin.count() == 0:
            emlto = EmailTo(id=emlid, to_=emladdr)
            emrdbs.add(emlto)
        else:
            logger.warning('Email-To repetido en la base de datos: Email de {} el {}'.format(emldta[4], fch.strftime(
                '%d-%m-%Y %H:%M:%S')))
    for emladdr in emldta[1]:
        twin = emrdbs.query(EmailFrom.id).filter_by(id=emlid, frm=emladdr)
        if twin.count() == 0:
            emlfrom = EmailFrom(id=emlid, frm=emladdr)
            emrdbs.add(emlfrom)
        else:
            logger.warning('Email-From repetido en la base de datos: Email de {} el {}'.format(emldta[4], fch.strftime(
                '%d-%m-%Y %H:%M:%S')))
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
    alerta_doble = False
    if twin.count() != 0:
        twin = emrdbs.query(Email.cliente).filter_by(id=twin.one()[0])
        if twin.count() != 0:
            cte = twin.one()[0]
            if emldta[4] == cte:
                alerta_doble = True
    if not alerta_doble:
        alert = Alerta(id=emlid, alert_details=tokens[0], start_datetime=sdt, end_datetime=edt, managed_object=tokens[3],
                       category_=tokens[4], rating=tokens[5], status=tokens[6], description=tokens[7],
                       analysis_tools=tokens[8])
        emrdbs.add(alert)
    else:
        logger.warning('Alerta ya se encuentra en la base de datos: Email de {} el {}'.format(emldta[4], fch.strftime(
            '%d-%m-%Y %H:%M:%S')))
    emrdbs.commit()


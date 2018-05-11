from emapp.models import Email, EmailFrom, EmailTo, Alerta
from emapp import emrdb
from datetime import datetime


def storedata(emldta, tokens):
    qryemlid = emrdb.session.query(emrdb.func.max(Email.id)).one()
    if qryemlid[0] is not None:
        emlid = qryemlid[0] + 1
    else:
        emlid = 1
    fch = datetime.strptime(emldta[3], '%d-%m-%Y %H:%M:%S')
    eml = Email(id=emlid, asunto=emldta[2], fecha=fch, cliente=emldta[4], idmsg=emldta[5])
    emrdb.session.add(eml)
    for emladdr in emldta[0]:
        emlto = EmailTo(id=emlid, to=emladdr)
        emrdb.session.add(emlto)
    for emladdr in emldta[1]:
        emlfrom = EmailFrom(id=emlid, frm=emladdr)
        emrdb.session.add(emlfrom)
    try:
        sdt = datetime.strptime(tokens[1], '%d-%m-%Y %H:%M:%S')
    except:
        sdt = datetime.strptime('01-01-1901 0:01:00', '%d-%m-%Y %H:%M:%S')
    try:
        edt = datetime.strptime(tokens[2], '%d-%m-%Y %H:%M:%S')
    except:
        edt = datetime.strptime('01-01-1901 0:01:00', '%d-%m-%Y %H:%M:%S')
    alert = Alerta(id=emlid, alert_details=tokens[0], start_datetime=sdt, end_datetime=edt, managed_object=tokens[3],
                   category=tokens[4], rating=tokens[5], status=tokens[6], description=tokens[7],
                   analysis_tools=tokens[8])
    emrdb.session.add(alert)
    emrdb.session.commit()

from emapp import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean


class Email(Base):
    __tablename__ = 'email'
    id = Column(Integer, primary_key=True)
    asunto = Column(String)
    fecha = Column(DateTime)
    cliente = Column(String)
    idmsg = Column(String)


class EmailFrom(Base):
    __tablename__ = 'email_from'
    id = Column(Integer, primary_key=True)
    frm = Column('from', String, primary_key=True, nullable=True)


class EmailTo(Base):
    __tablename__ = 'email_to'
    id = Column(Integer, primary_key=True)
    to = Column(String, primary_key=True, nullable=True)


class Alerta(Base):
    __tablename__ = 'alerta'
    id = Column(Integer, primary_key=True)
    alert_details = Column(String)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    managed_object = Column(String)
    category = Column(String)
    rating = Column(String)
    status = Column(String)
    description = Column(String)
    analysis_tools = Column(String)


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    running = Column(Boolean)

    def __repr__(self):
        return '<Corriendo: {}>'.format(self.running)

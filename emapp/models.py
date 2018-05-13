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
    frm = Column('frm', String, primary_key=True, nullable=True)


class EmailTo(Base):
    __tablename__ = 'email_to'
    id = Column(Integer, primary_key=True)
    to_ = Column(String, primary_key=True, nullable=True)


class Alerta(Base):
    __tablename__ = 'alerta'
    id = Column(Integer, primary_key=True)
    alert_details = Column(String)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    managed_object = Column(String)
    category_ = Column(String)
    rating = Column(String)
    status = Column(String)
    description = Column(String)
    analysis_tools = Column(String)

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey,
    Numeric
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Parcours(Base):
    __tablename__ = 'parcours'
    id = Column(Integer, primary_key=True)
    nom = Column(Text)
    contenu = Column(Text)
    proposes = relationship(
        "Etudiant", backref="etudiants_proposes", foreign_keys='Etudiant.proposition')
    affectes = relationship(
        "Etudiant", backref="etudiants_affectes", foreign_keys='Etudiant.affectation')


class Etudiant(Base):
    __tablename__ = 'etudiant'
    id = Column(Integer, primary_key=True)
    nom = Column(Text)
    email = Column(Text)
    projetPro = Column(Text)
    appel = Column(Text)
    voeu = relationship("Voeu", backref="etudiant")
    proposition = Column(Integer, ForeignKey('parcours.id'))
    affectation = Column(Integer, ForeignKey('parcours.id'))
    moyenneMaths = Column(Numeric)
    malus = Column(Integer)
    enseignant = Column(Integer)
    absences = Column(Integer)


class Voeu(Base):
    __tablename__ = 'voeu'
    idParcours = Column(Integer, ForeignKey('parcours.id'), primary_key=True)
    idEtudiant = Column(Integer, ForeignKey('etudiant.id'), primary_key=True)
    rang = Column(Integer, default=-1)
    parcours = relationship("Parcours", backref="etudiant_assoc")


Index('my_index', Etudiant.email, unique=True, mysql_length=255)

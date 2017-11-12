# -*- coding: utf-8 -*-

"""Reactome database model"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

Base = declarative_base()

TABLE_PREFIX = 'chebi'
CHEMICAL_TABLE_NAME = '{}_chemical'.format(TABLE_PREFIX)
SYNONYM_TABLE_NAME = '{}_synonym'.format(TABLE_PREFIX)
ACCESSION_TABLE_NAME = '{}_accession'.format(TABLE_PREFIX)


class Chemical(Base):
    """Represents a chemical"""
    __tablename__ = CHEMICAL_TABLE_NAME

    id = Column(Integer, primary_key=True)

    chebi_id = Column(Integer, nullable=False, unique=True, index=True)

    status = Column(String(8))

    parent_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)))
    #parent = relationship('Chemical', backref=backref('children'), uselist=False)

    name = Column(Text)
    definition = Column(Text)

    source = Column(Text)

    inchi = Column(Text)

    def __str__(self):
        return str(self.chebi_id)


class Synonym(Base):
    """Represents synonyms of a chemical"""
    __tablename__ = SYNONYM_TABLE_NAME

    id = Column(Integer, primary_key=True)

    chemical_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)))
    chemical = relationship('Chemical', backref=backref('synonyms'))

    type = Column(String(16), doc='One of: NAME, SYNONYM, IUPAC NAME, INN, BRAND NAME')
    source = Column(String(32))
    name = Column(Text)
    adapted = Column(Text)
    language = Column(String(8))


    # index on ID/Source
    # index on id/name/source


class Accession(Base):
    __tablename__ = ACCESSION_TABLE_NAME

    id = Column(Integer, primary_key=True)

    chemical_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)))
    chemical = relationship('Chemical', backref=backref('accessions'))

    source = Column(String(255))
    type = Column(String(255))
    accession = Column(String(255))
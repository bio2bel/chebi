# -*- coding: utf-8 -*-

"""ChEBI database model"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from pybel.dsl import abundance

__all__ = [
    'Base',
    'Chemical',
    'Synonym',
    'Accession',
]

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
    parent = relationship('Chemical', remote_side=[id], backref=backref('children'), uselist=False)

    name = Column(Text, index=True)
    definition = Column(Text)

    source = Column(Text)

    inchi = Column(Text)

    def __str__(self):
        return str(self.chebi_id)

    def to_json(self, include_id=True):
        rv = {
            'chebi_id': self.chebi_id,
            'name': self.name,
            'definition': self.definition,
            'source': self.source,
            'inchi': self.inchi,
        }

        if include_id:
            rv['id'] = self.id

        return rv

    def to_bel(self):
        """Makes an abundance PyBEL data dictionary

        :rtype: abundance
        """
        return abundance(
            namespace='CHEBI',
            name=str(self.name),
            identifier=str(self.chebi_id)
        )


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

    def __str__(self):
        return self.name


class Accession(Base):
    __tablename__ = ACCESSION_TABLE_NAME

    id = Column(Integer, primary_key=True)

    chemical_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)))
    chemical = relationship('Chemical', backref=backref('accessions'))

    source = Column(String(255))
    type = Column(String(255))
    accession = Column(String(255))

    def __str__(self):
        return '{}:{}'.format(self.source, self.accession)

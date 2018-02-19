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


# FIXME need chemical multi-hierarchy?

class Chemical(Base):
    """Represents a chemical"""
    __tablename__ = CHEMICAL_TABLE_NAME

    id = Column(Integer, primary_key=True)

    chebi_id = Column(String(32), nullable=False, unique=True, index=True, doc='The ChEBI identifier for a compound')

    parent_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)), doc='The parent chemical')
    parent = relationship('Chemical', remote_side=[id], backref=backref('children'), uselist=False)

    name = Column(String(3071), index=True, doc='The name of the compound')
    definition = Column(Text, doc='A description of the compound')
    source = Column(Text, doc='The database source')
    status = Column(String(8))
    inchi = Column(Text, doc='The InChI string for this compound')

    def __repr__(self):
        return '<Chemical CHEBI:{}>'.format(self.chebi_id)

    def __str__(self):
        return str(self.name)

    def to_json(self, include_id=False):
        """
        :param bool include_id: Include the database identifier?
        :rtype: dict
        """
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
    """Represents related accession numbers of a chemical"""
    __tablename__ = ACCESSION_TABLE_NAME

    id = Column(Integer, primary_key=True)

    chemical_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)))
    chemical = relationship('Chemical', backref=backref('accessions'))

    source = Column(String(255))
    type = Column(String(255))
    accession = Column(String(255))

    def __str__(self):
        return '{}:{}'.format(self.source, self.accession)

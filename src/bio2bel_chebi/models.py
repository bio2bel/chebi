# -*- coding: utf-8 -*-

"""SQLAlchemy models for Bio2BEL ChEBI."""

from sqlalchemy import Column, Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from pybel.constants import NAME, PART_OF
from pybel.dsl import abundance

__all__ = [
    'Base',
    'Chemical',
    'Synonym',
    'Accession',
    'Relation',
]

Base = declarative_base()

TABLE_PREFIX = 'chebi'
CHEMICAL_TABLE_NAME = '{}_chemical'.format(TABLE_PREFIX)
SYNONYM_TABLE_NAME = '{}_synonym'.format(TABLE_PREFIX)
ACCESSION_TABLE_NAME = '{}_accession'.format(TABLE_PREFIX)
RELATION_TABLE_NAME = '{}_relation'.format(TABLE_PREFIX)


class Chemical(Base):
    """Represents a chemical"""
    __tablename__ = CHEMICAL_TABLE_NAME

    id = Column(Integer, primary_key=True)

    chebi_id = Column(String(32), nullable=False, unique=True, index=True, doc='The ChEBI identifier for a compound')

    parent_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)), nullable=True)
    children = relationship('Chemical', backref=backref('parent', remote_side=[id]))

    name = Column(String(2000), doc='The name of the compound')
    definition = Column(Text, doc='A description of the compound')
    source = Column(Text, doc='The database source')
    status = Column(String(8))
    inchi = Column(Text, doc='The InChI string for this compound')
    modified_on = Column(Date)
    created_by = Column(String(255))
    stars = Column(Integer)

    def __repr__(self):
        return '<Chemical CHEBI:{}>'.format(self.chebi_id)

    def __str__(self):
        return self.safe_name or self.chebi_id

    @property
    def safe_name(self):
        """Either returns this molecule's name, or the parent name

        :rtype: str
        """
        return self.name or self.parent.name

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
        if self.parent:
            return self.parent.to_bel()

        return abundance(
            namespace='CHEBI',
            name=self.name,
            identifier=self.chebi_id
        )


class Relation(Base):
    """Represents a relation between two chemicals"""
    __tablename__ = RELATION_TABLE_NAME

    id = Column(Integer, primary_key=True)

    type = Column(String(32), nullable=False, index=True)
    status = Column(String(1), nullable=False, index=True)

    source_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)), nullable=False)
    source = relationship('Chemical', foreign_keys=[source_id], backref=backref('out_edges', lazy='dynamic'))

    target_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)), nullable=False)
    target = relationship('Chemical', foreign_keys=[target_id], backref=backref('in_edges', lazy='dynamic'))

    def add_to_graph(self, graph):
        """Add this relation to the graph

        :param pybel.BELGraph graph:
        :rtype: Optional[str]
        """
        source = self.source.to_bel()
        target = self.target.to_bel()

        if NAME not in source or NAME not in target:
            return

        if self.type == 'has_part':
            return graph.add_unqualified_edge(target, source, PART_OF)

        if self.type == 'is_a':
            return graph.add_is_a(target, source)


Index('relation_source_type_idx', Relation.source_id, Relation.type)
Index('relation_target_type_idx', Relation.target_id, Relation.type)


class Synonym(Base):
    """Represents synonyms of a chemical"""
    __tablename__ = SYNONYM_TABLE_NAME

    id = Column(Integer, primary_key=True)

    chemical_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)), nullable=False)
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

    chemical_id = Column(Integer, ForeignKey('{}.id'.format(CHEMICAL_TABLE_NAME)), nullable=False)
    chemical = relationship('Chemical', backref=backref('accessions'))

    source = Column(String(255))
    type = Column(String(255))
    accession = Column(String(255))

    def __str__(self):
        return '{}:{}'.format(self.source, self.accession)

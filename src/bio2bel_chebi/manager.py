# -*- coding: utf-8 -*-

import logging
import time

from bio2bel.utils import get_connection
from pybel.constants import IDENTIFIER, IS_A, NAME, NAMESPACE
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from .constants import MODULE_NAME
from .models import Accession, Base, Chemical, Synonym
from .parser.accession import get_accession_df
from .parser.compounds import get_compounds_df
from .parser.inchis import get_inchis_df
from .parser.names import get_names_df

__all__ = ['Manager']

log = logging.getLogger(__name__)


class Manager(object):
    def __init__(self, connection=None):
        self.connection = get_connection(MODULE_NAME, connection=connection)
        self.engine = create_engine(self.connection)
        self.session_maker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = self.session_maker()
        self.create_all()
        self.chemicals = {}

    @staticmethod
    def ensure(connection=None):
        """
        :param connection: A connection string, a manager, or none to use the default manager
        :type connection: Optional[str or Manager]
        :rtype: Manager
        """
        if connection is None or isinstance(connection, str):
            return Manager(connection=connection)
        return connection

    def create_all(self, check_first=True):
        """Create tables"""
        log.info('create table in {}'.format(self.engine.url))
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_all(self, check_first=True):
        """Create tables"""
        log.info('dropping table in {}'.format(self.engine.url))
        Base.metadata.drop_all(self.engine, checkfirst=check_first)

    def get_or_create_chemical(self, chebi_id, **kwargs):
        """Gets a chemical from the database by ChEBI

        :param str chebi_id: ChEBI database identifier
        :rtype: Chemical
        """
        if chebi_id in self.chemicals:
            return self.chemicals[chebi_id]

        chemical = self.get_chemical_by_chebi_id(chebi_id)

        if chemical is None:
            chemical = Chemical(chebi_id=chebi_id, **kwargs)

        self.chemicals[chebi_id] = chemical
        return chemical

    def get_chemical_by_chebi_id(self, chebi_id):
        """Get a chemical from the database

        :param str chebi_id: ChEBI database identifier
        :rtype: Optional[Chemical]
        """
        return self.session.query(Chemical).filter(Chemical.chebi_id == chebi_id).one_or_none()

    def get_chemical_by_chebi_name(self, name):
        """Get a chemical from the database

        :param str name: ChEBI name
        :rtype: Optional[Chemical]
        """
        return self.session.query(Chemical).filter(Chemical.name == name).one_or_none()

    def build_chebi_id_name_mapping(self):
        """Builds a mapping from CHEBI identifier to CHEBI name
        :rtype: dict[str,str]
        """
        return {
            str(identifier): name
            for identifier, name in self.session.query(Chemical.id, Chemical.name).all()
        }

    def build_chebi_name_id_mapping(self):
        """Builds a mapping from CHEBI name to CHEBI identifier
        :rtype: dict[str,str]
        """
        return {
            name: str(identifier)
            for name, identifier in self.session.query(Chemical.name, Chemical.id).all()
        }

    def _populate_compounds(self, url=None):
        """Downloads and populates the compounds

        :param Optional[str] url:
        """
        log.info('Downloading compounds')

        df = get_compounds_df(url=url)

        log.info('Inserting compounds')

        for _, (_, status, chebi_id, source, parent_id, name, definition, _, _, _) in tqdm(df.iterrows(),
                                                                                           desc='Inserting compounds',
                                                                                           total=len(df.index)):
            chemical = Chemical(
                status=status,
                chebi_id=chebi_id.split(':')[1],
                parent_id=parent_id,
                name=name,
                definition=definition
            )
            self.session.add(chemical)

        self.session.commit()

    def _populate_inchis(self, url=None):
        """Downloads and inserts the InChI strings

        :param Optional[str] url:
        """
        log.info('Downloading inchis')
        df = get_inchis_df(url=url)

        log.info('Inserting inchis')
        for _, (chebi_id, inchi) in tqdm(df.iterrows(), desc='Inserting InChIs', total=len(df.index)):
            chemical = self.get_or_create_chemical(chebi_id=chebi_id)
            chemical.inchi = inchi
            self.session.add(chemical)

        self.session.commit()

    def _populate_names(self, url=None):
        """Downloads and inserts the synonyms

        :param Optional[str] url:
        """
        log.info('Downloading names')
        df = get_names_df(url=url)

        log.info('Inserting names')
        for _, (_, chebi_id, type, source, name, adapted, language) in tqdm(df.iterrows(), desc='Inserting synonyms',
                                                                            total=len(df.index)):
            synonym = Synonym(
                chemical=self.get_or_create_chemical(chebi_id=chebi_id),
                type=type,
                source=source,
                name=name,
                language=language
            )
            self.session.add(synonym)

        self.session.commit()

    def _populate_accession(self, url=None):
        """Downloads and inserts the database cross references and accession numbers

        :param Optional[str] url:
        """
        log.info('Downloading accessions')
        df = get_accession_df(url=url)

        log.info('Inserting accessions')

        for _, (_, chebi_id, source, type, accession) in tqdm(df.iterrows(), desc='Inserting accessions',
                                                              total=len(df.index)):
            acc = Accession(
                chemical=self.get_or_create_chemical(chebi_id=chebi_id),
                source=source,
                type=type,
                accession=accession
            )
            self.session.add(acc)

        self.session.commit()

    def populate(self):
        """Populates all tables"""
        t = time.time()

        self._populate_compounds()
        self._populate_inchis()
        self._populate_names()
        self._populate_accession()

        log.info('populated in %.2f seconds', time.time() - t)

    def enrich_chemical_hierarchy(self, graph):
        """Enriches the parents for all ChEBI chemicals in the graph

        :type graph: pybel.BELGraph
        """
        for node, data in graph.nodes_iter(data=True):
            namespace = data.get(NAMESPACE)

            if namespace not in {'CHEBI', 'CHEBIID'}:
                continue

            identifier = data.get(IDENTIFIER)
            name = data.get(NAME)

            if namespace == 'CHEBI':
                if identifier is not None:
                    m = self.get_chemical_by_chebi_id(identifier)
                elif name is not None:
                    m = self.get_chemical_by_chebi_name(name)
                else:
                    raise ValueError

            elif namespace == 'CHEBIID':
                m = self.get_chemical_by_chebi_id(name)

            else:
                continue

            parent = m.parent

            if parent is None:
                continue

            graph.add_unqualified_edge(
                node,
                parent.as_bel(),
                IS_A
            )

    def to_bel(self):
        raise NotImplementedError

# -*- coding: utf-8 -*-

import logging
import pandas as pd
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from bio2bel.utils import get_connection
from pybel.constants import IDENTIFIER, NAME, NAMESPACE
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

        self.id_chemical = {}
        self.id_inchi = {}

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
        log.info('create tables in {}'.format(self.engine.url))
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_all(self, check_first=True):
        """Create tables"""
        log.info('dropping tables in {}'.format(self.engine.url))
        Base.metadata.drop_all(self.engine, checkfirst=check_first)

    def count_chemicals(self):
        """Counts the number of chemicals stored

        :rtype: int
        """
        return self.session.query(Chemical).count()

    def count_xrefs(self):
        """Counts the number of cross-references stored

        :rtype: int
        """
        return self.session.query(Accession).count()

    def count_synonyms(self):
        """Counts the number of synonyms stored

        :rtype: int
        """
        return self.session.query(Synonym).count()

    def get_or_create_chemical(self, chebi_id, **kwargs):
        """Gets a chemical from the database by ChEBI

        :param str chebi_id: ChEBI database identifier
        :rtype: Chemical
        """
        chemical = self.id_chemical.get(chebi_id)

        if chemical is not None:
            return chemical

        chemical = self.get_chemical_by_chebi_id(chebi_id)

        if chemical is None:
            chemical = Chemical(chebi_id=chebi_id, **kwargs)

        self.id_chemical[chebi_id] = chemical
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
        """Builds a mapping from ChEBI identifier to ChEBI name

        :rtype: dict[str,str]
        """
        return dict(self.session.query(Chemical.chebi_id, Chemical.name).all())

    def build_chebi_name_id_mapping(self):
        """Builds a mapping from ChEBI name to ChEBI identifier

        :rtype: dict[str,str]
        """
        return dict(self.session.query(Chemical.name, Chemical.chebi_id).all())

    def _populate_inchis(self, url=None):
        """Downloads and inserts the InChI strings

        :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
        """
        df = get_inchis_df(url=url)

        for _, (chebi_id, inchi) in tqdm(df.iterrows(), desc='InChIs', total=len(df.index)):
            self.id_inchi[str(chebi_id)] = inchi

    def _populate_compounds(self, url=None):
        """Downloads and populates the compounds

        :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
        """
        df = get_compounds_df(url=url)
        df = df.where((pd.notnull(df)), None)

        log.info('preparing Compounds')

        parents = []
        for _, (_, status, chebi_id, source, parent_id, name, definition, _, _, _) in tqdm(df.iterrows(),
                                                                                           desc='Compounds',
                                                                                           total=len(df.index)):
            chebi_id = chebi_id.split(':')[1]

            chemical = self.id_chemical[chebi_id] = Chemical(
                status=status,
                chebi_id=chebi_id,
                name=name,
                source=source,
                definition=definition,
                inchi=self.id_inchi.get(chebi_id)
            )
            self.session.add(chemical)

            if parent_id:
                parents.append((chebi_id, parent_id))

        for child_id, parent_id in tqdm(parents, desc='Hierarchy'):
            child = self.id_chemical.get(child_id)
            parent = self.id_chemical.get(parent_id)

            if child and parent:
                child.parent_id = parent.id

        log.info('committing Compounds')
        self.session.commit()

    def _populate_names(self, url=None):
        """Downloads and inserts the synonyms

        :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
        """
        df = get_names_df(url=url)

        log.info('preparing Synonyms')
        grouped_df = df.groupby('COMPOUND_ID')
        for chebi_id, sub_df in tqdm(grouped_df, desc='Synonyms', total=len(grouped_df)):
            chebi_id = str(int(chebi_id))
            chemical = self.get_or_create_chemical(chebi_id=chebi_id)

            for _, (_, chebi_id, type_, source, name, adapted, language) in sub_df.iterrows():

                if isinstance(name, float) or not name:
                    continue

                synonym = Synonym(
                    chemical=chemical,
                    type=type_,
                    source=source,
                    name=name,
                    language=language
                )
                self.session.add(synonym)

        log.info('committing Synonyms')
        self.session.commit()

    def _populate_accession(self, url=None):
        """Downloads and inserts the database cross references and accession numbers

        :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
        """
        df = get_accession_df(url=url)
        df = df.where((pd.notnull(df)), None)

        log.info('preparing Accessions')

        grouped_df = df.groupby('COMPOUND_ID')
        for chebi_id, sub_df in tqdm(grouped_df, desc='Synonyms', total=len(grouped_df)):
            chebi_id = str(int(chebi_id))
            chemical = self.get_or_create_chemical(chebi_id=chebi_id)
            for _, (_, chebi_id, source, type_, accession) in sub_df.iterrows():
                acc = Accession(
                    chemical=chemical,
                    source=source,
                    type=type_,
                    accession=accession
                )
                self.session.add(acc)

        log.info('committing Accessions')
        self.session.commit()

    def populate(self):
        """Populates all tables"""
        t = time.time()

        self._populate_inchis()
        self._populate_compounds()
        self._populate_names()
        self._populate_accession()

        log.info('populated in %.2f seconds', time.time() - t)

    def get_chemical_from_data(self, data):
        namespace = data.get(NAMESPACE)

        if namespace not in {'CHEBI', 'CHEBIID'}:
            return

        identifier = data.get(IDENTIFIER)
        name = data.get(NAME)

        if namespace == 'CHEBI':
            if identifier is not None:
                return self.get_chemical_by_chebi_id(identifier)

            if name is not None:
                return self.get_chemical_by_chebi_name(name)

            else:
                raise ValueError

        elif namespace == 'CHEBIID':
            return self.get_chemical_by_chebi_id(name)

    def enrich_chemical_hierarchy(self, graph):
        """Enriches the parents for all ChEBI chemicals in the graph

        :type graph: pybel.BELGraph
        """
        for node, data in graph.nodes_iter(data=True):
            m = self.get_chemical_from_data(data)

            if m is None:
                continue

            parent = m.parent

            if parent is None:
                continue

            graph.add_is_a(node, parent.as_bel())

# -*- coding: utf-8 -*-


import logging
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from bio2bel.utils import get_connection
from .constants import MODULE_NAME
from .models import Accession, Base, Chemical, Synonym
from .parser.accession import get_accession_df
from .parser.compounds import get_compounds_df
from .parser.inchis import get_inchis_df
from .parser.names import get_names_df

log = logging.getLogger(__name__)


class Manager(object):
    def __init__(self, connection=None):
        self.connection = get_connection(MODULE_NAME, connection=connection)
        self.engine = create_engine(self.connection)
        self.session_maker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = self.session_maker()
        self.create_all()
        self.chemicals = {}

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


if __name__ == '__main__':
    logging.basicConfig(level=10)
    log.setLevel(10)

    from bio2bel_chebi.constants import DEFAULT_CACHE_LOCATION
    import os

    os.remove(DEFAULT_CACHE_LOCATION)

    m = Manager()
    m.populate()

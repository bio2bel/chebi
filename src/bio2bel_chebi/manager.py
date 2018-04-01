# -*- coding: utf-8 -*-

import logging
import time

import pandas as pd
from tqdm import tqdm

import pybel
from bio2bel.abstractmanager import AbstractManager
from bio2bel.utils import bio2bel_populater
from pybel.constants import IDENTIFIER, NAME, NAMESPACE
from .constants import MODULE_NAME
from .models import Accession, Base, Chemical, Synonym, Relation
from .parser.accession import get_accession_df
from .parser.compounds import get_compounds_df
from .parser.inchis import get_inchis_df
from .parser.names import get_names_df
from .parser.relation import get_relations_df

__all__ = ['Manager']

log = logging.getLogger(__name__)


class Manager(AbstractManager):
    """Bio2BEL ChEBI Manager"""

    module_name = MODULE_NAME
    flask_admin_models = [Chemical, Relation, Synonym, Accession]

    def __init__(self, connection=None):
        super().__init__(connection=connection)


        self.chebi_id_to_chemical = {}
        self.chebi_id_to_inchi = {}

    @property
    def base(self):
        return Base

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

    def summarize(self):
        """Returns a summary dictionary over the content of the database

        :rtype: dict[str,int]
        """
        return dict(
            chemicals=self.count_chemicals(),
            xrefs=self.count_xrefs(),
            synonyms=self.count_synonyms()
        )

    def get_or_create_chemical(self, chebi_id, **kwargs):
        """Gets a chemical from the database by ChEBI

        :param str chebi_id: ChEBI database identifier
        :rtype: Chemical
        """
        chemical = self.chebi_id_to_chemical.get(chebi_id)

        if chemical is not None:
            return chemical

        chemical = self.get_chemical_by_chebi_id(chebi_id)

        if chemical is None:
            chemical = Chemical(chebi_id=chebi_id, **kwargs)

        self.chebi_id_to_chemical[chebi_id] = chemical
        return chemical

    def get_chemical_by_chebi_id(self, chebi_id):
        """Get a chemical from the database

        :param str chebi_id: ChEBI database identifier
        :rtype: Optional[Chemical]
        """
        chemical = self.session.query(Chemical).filter(Chemical.chebi_id == chebi_id).one_or_none()
        if chemical.parent:
            return chemical.parent
        return chemical

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
        # FIXME handle secondary id to correct name mappings, since the name isn't stored with the secondary id entry
        return dict(self.session.query(Chemical.chebi_id, Chemical.name).all())

    def build_chebi_name_id_mapping(self):
        """Builds a mapping from ChEBI name to ChEBI identifier

        :rtype: dict[str,str]
        """
        return dict(self.session.query(Chemical.name, Chemical.chebi_id).all())

    def _load_inchis(self, url=None):
        """Downloads and inserts the InChI strings

        :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
        """
        df = get_inchis_df(url=url)

        for _, (chebi_id, inchi) in tqdm(df.iterrows(), desc='InChIs', total=len(df.index)):
            self.chebi_id_to_inchi[str(chebi_id)] = inchi

    def _populate_compounds(self, url=None):
        """Downloads and populates the compounds

        :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
        """
        df = get_compounds_df(url=url)
        df = df.where((pd.notnull(df)), None)

        log.info('preparing Compounds')

        parents = []
        it = tqdm(df.iterrows(), desc='Compounds', total=len(df.index))
        for _, (pk, status, chebi_id, source, parent_chebi_id, name, definition, _, _, _) in it:
            chebi_id = chebi_id.split(':')[1]

            chemical = self.chebi_id_to_chemical[chebi_id] = Chemical(
                id=pk,  # ChEBI already sends out their data in relational format
                status=status,
                chebi_id=chebi_id,
                parent_chebi_id=parent_chebi_id or None,
                name=name,
                source=source,
                definition=definition,
                inchi=self.chebi_id_to_inchi.get(chebi_id)
            )
            self.session.add(chemical)

            if parent_chebi_id:
                parents.append((chebi_id, parent_chebi_id))

        for child_id, parent_chebi_id in tqdm(parents, desc='Secondaries'):
            child = self.chebi_id_to_chemical.get(child_id)
            parent = self.chebi_id_to_chemical.get(parent_chebi_id)

            if child is not None and parent is not None:
                child.parent = parent

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

            for _, (pk, chebi_id, type_, source, name, adapted, language) in sub_df.iterrows():

                if isinstance(name, float) or not name:
                    continue

                synonym = Synonym(
                    id=pk,
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
        for chebi_id, sub_df in tqdm(grouped_df, desc='Xrefs', total=len(grouped_df)):
            chebi_id = str(int(chebi_id))
            chemical = self.get_or_create_chemical(chebi_id=chebi_id)
            for _, (pk, chebi_id, source, type_, accession) in sub_df.iterrows():
                acc = Accession(
                    id=pk,
                    chemical=chemical,
                    source=source,
                    type=type_,
                    accession=accession
                )
                self.session.add(acc)

        log.info('committing Accessions')
        self.session.commit()

    def _populate_relations(self, url=None):
        """

        :param Optional[str] url:
        """
        df = get_relations_df(url=url)

        for _, (pk, relation_type, source_id, target_id, status)  in tqdm(df.iterrows(), total=len(df.index)):
            relation = Relation(
                id=pk,
                type=relation_type,
                source_id=source_id,
                target_id=target_id,
                status=status,
            )
            self.session.add(relation)

        log.info('committing Relations')
        self.session.commit()

    @bio2bel_populater(MODULE_NAME)
    def populate(self):
        """Populates all tables"""
        t = time.time()

        self._load_inchis()
        self._populate_compounds()
        self._populate_relations()
        # self._populate_names()
        # self._populate_accession()

        log.info('populated in %.2f seconds', time.time() - t)

    def get_chemical_from_data(self, data):
        """

        :param dict data:
        :rtype: Optional[Chemical]
        """
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
        for _, data in graph.nodes(data=True):
            chemical = self.get_chemical_from_data(data)

            if chemical is None:
                continue

            parent = chemical.parent
            while parent is not None:
                graph.add_is_a(chemical.as_bel(), parent.as_bel())
                chemical, parent = parent, parent.parent

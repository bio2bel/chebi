# -*- coding: utf-8 -*-

"""Manager for Bio2BEL ChEBI."""

import datetime
import logging
import time
from typing import List, Mapping, Optional

import pandas as pd
from tqdm import tqdm

from bio2bel import AbstractManager
from bio2bel.manager.flask_manager import FlaskMixin
from bio2bel.manager.namespace_manager import BELNamespaceManagerMixin
from pybel import BELGraph
from pybel.constants import IDENTIFIER, NAME, NAMESPACE
from pybel.dsl import BaseEntity
from pybel.manager.models import Namespace, NamespaceEntry
from .constants import MODULE_NAME
from .models import Accession, Base, Chemical, Relation, Synonym
from .parser.accession import get_accession_df
from .parser.compounds import get_compounds_df
from .parser.inchis import get_inchis_df
from .parser.names import get_names_df
from .parser.relation import get_relations_df

__all__ = ['Manager']

log = logging.getLogger(__name__)

_chebi_bel_name = 'ChEBI Ontology'
_chebi_bel_version = datetime.datetime.utcnow().strftime('%Y%m%d%H%M')
_chebi_description = 'Relations between chemicals of biological interest'


class Manager(AbstractManager, FlaskMixin, BELNamespaceManagerMixin):
    """Bio2BEL ChEBI Manager."""

    _base = Base
    module_name = MODULE_NAME

    namespace_model = Chemical
    identifiers_recommended = 'ChEBI'
    identifiers_pattern = r'^CHEBI:\d+$'
    identifiers_miriam = 'MIR:00000002'
    identifiers_namespace = 'chebi'
    identifiers_url = 'http://identifiers.org/chebi/'

    flask_admin_models = [Chemical, Relation, Synonym, Accession]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # a dictionary from CHEBI identifier (string CHEBI:\d+) to the model
        self.id_chemical = {}
        self.chebi_id_to_chemical = {}
        self.chebi_id_to_inchi = {}

    def is_populated(self) -> bool:
        """Check if the database is already populated."""
        return 0 < self.count_chemicals()

    def count_chemicals(self) -> int:
        """Count the number of chemicals stored."""
        return self.session.query(Chemical).count()

    def count_parent_chemicals(self) -> int:
        """Count the number of parent chemicals stored."""
        return self.session.query(Chemical).filter(Chemical.parent_id.is_(None)).count()

    def count_child_chemicals(self) -> int:
        """Count the number of child chemicals stored."""
        return self.session.query(Chemical).filter(Chemical.parent_id.isnot(None)).count()

    def count_xrefs(self) -> int:
        """Count the number of cross-references stored."""
        return self.session.query(Accession).count()

    def count_synonyms(self) -> int:
        """Count the number of synonyms stored."""
        return self.session.query(Synonym).count()

    def count_inchis(self) -> int:
        """Count the number of inchis stored."""
        return self.session.query(Chemical).filter(Chemical.inchi.isnot(None)).count()

    def count_relations(self) -> int:
        """Count the relations in the database."""
        return self._count_model(Relation)

    def list_relations(self) -> List[Relation]:
        """List the relations in the database."""
        return self.session.query(Relation).all()

    def summarize(self) -> Mapping[str, int]:
        """Return a summary dictionary over the content of the database."""
        return dict(
            chemicals=self.count_chemicals(),
            xrefs=self.count_xrefs(),
            relations=self.count_relations(),
            synonyms=self.count_synonyms(),
        )

    def get_or_create_chemical(self, chebi_id: str, **kwargs) -> Chemical:
        """Get a chemical from the database by ChEBI."""
        chemical = self.chebi_id_to_chemical.get(chebi_id)

        if chemical is not None:
            return chemical

        chemical = self.get_chemical_by_chebi_id(chebi_id)

        if chemical is None:
            chemical = Chemical(chebi_id=chebi_id, **kwargs)

        self.chebi_id_to_chemical[chebi_id] = chemical
        return chemical

    def get_chemical_by_chebi_id(self, chebi_id: str) -> Optional[Chemical]:
        """Get a chemical from the database."""
        chemical = self.session.query(Chemical).filter(Chemical.chebi_id == chebi_id).one_or_none()

        if not chemical:
            return None

        if chemical.parent:
            return chemical.parent

        return chemical

    def get_chemical_by_chebi_name(self, name: str) -> Optional[Chemical]:
        """Get a chemical from the database."""
        return self.session.query(Chemical).filter(Chemical.name == name).one_or_none()

    def build_chebi_id_name_mapping(self) -> Mapping[str, str]:
        """Build a mapping from ChEBI identifier to ChEBI name."""
        # FIXME handle secondary id to correct name mappings, since the name isn't stored with the secondary id entry
        return dict(self.session.query(Chemical.chebi_id, Chemical.name).all())

    def build_chebi_name_id_mapping(self) -> Mapping[str, str]:
        """Build a mapping from ChEBI name to ChEBI identifier."""
        return dict(self.session.query(Chemical.name, Chemical.chebi_id).all())

    def _load_inchis(self, url: Optional[str] = None) -> None:
        """Download and insert the InChI strings.

        :param url: The URL (or file path) to download. Defaults to the ChEBI data.
        """
        df = get_inchis_df(url=url)

        for _, (chebi_id, inchi) in tqdm(df.iterrows(), desc='InChIs', total=len(df.index)):
            self.chebi_id_to_inchi[str(chebi_id)] = inchi

    def _populate_compounds(self, url: Optional[str] = None) -> None:
        """Download and populate the compounds.

        :param url: The URL (or file path) to download. Defaults to the ChEBI data.
        """
        df = get_compounds_df(url=url)
        df = df.where((pd.notnull(df)), None)

        log.info('preparing Compounds')

        parents = []
        it = tqdm(df.iterrows(), desc='Compounds', total=len(df.index))
        for _, (pk, status, chebi_id, source, parent_pk, name, definition, _, _, _) in it:
            chebi_id = chebi_id.split(':')[1]

            chemical = self.id_chemical[pk] = self.chebi_id_to_chemical[chebi_id] = Chemical(
                id=pk,  # ChEBI already sends out their data in relational format
                status=status,
                chebi_id=chebi_id,
                parent_id=parent_pk or None,
                name=name,
                source=source,
                definition=definition,
                inchi=self.chebi_id_to_inchi.get(chebi_id)
            )
            self.session.add(chemical)

            if parent_pk:
                parents.append((pk, parent_pk))

        for child_id, parent_pk in tqdm(parents, desc='Secondaries'):
            child = self.chebi_id_to_chemical.get(child_id)
            parent = self.chebi_id_to_chemical.get(parent_pk)

            if child is not None and parent is not None:
                child.parent = parent

        log.info('committing Compounds')
        self.session.commit()

    def _populate_names(self, url: Optional[str] = None) -> None:
        """Download and insert the synonyms.

        :param url: The URL (or file path) to download. Defaults to the ChEBI data.
        """
        df = get_names_df(url=url)

        log.info('preparing Synonyms')
        grouped_df = df.groupby('COMPOUND_ID')
        for chebi_id, sub_df in tqdm(grouped_df, desc='Synonyms', total=len(grouped_df)):
            chebi_id = str(int(chebi_id))
            chemical = self.get_or_create_chemical(chebi_id=chebi_id)

            for _, (pk, _, type_, source, name, adapted, language) in sub_df.iterrows():

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

    def _populate_accession(self, url: Optional[str] = None) -> None:
        """Download and inserts the database cross references and accession numbers

        :param url: The URL (or file path) to download. Defaults to the ChEBI data.
        """
        df = get_accession_df(url=url)
        df = df.where((pd.notnull(df)), None)

        log.info('preparing Accessions')

        grouped_df = df.groupby('COMPOUND_ID')
        for chebi_id, sub_df in tqdm(grouped_df, desc='Xrefs', total=len(grouped_df)):
            chebi_id = str(int(chebi_id))
            chemical = self.get_or_create_chemical(chebi_id=chebi_id)
            for _, (pk, _, source, type_, accession) in sub_df.iterrows():
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

    def _populate_relations(self, url: Optional[str] = None) -> None:
        df = get_relations_df(url=url)
        for _, (pk, relation_type, source_id, target_id, status) in tqdm(df.iterrows(), total=len(df.index)):

            source = self.id_chemical.get(f'CHEBI:{source_id}')

            if source is None:
                continue

            target = self.id_chemical.get(f'CHEBI:{target_id}')

            if target is None:
                continue

            relation = Relation(
                id=pk,
                type=relation_type,
                source=source,
                target=target,
                status=status,
            )
            self.session.add(relation)

        log.info('committing Relations')
        self.session.commit()

    def populate(self,
                 inchis_url: Optional[str] = None,
                 compounds_url: Optional[str] = None,
                 relations_url: Optional[str] = None,
                 names_url: Optional[str] = None,
                 accessions_url: Optional[str] = None,
                 ) -> None:
        """Populate all tables."""
        t = time.time()

        self._load_inchis(url=inchis_url)
        self._populate_compounds(url=compounds_url)
        # self._populate_relations(url=relations_url)
        # self._populate_names(url=names_url)
        # self._populate_accession(url=accessions_url)

        log.info('populated in %.2f seconds', time.time() - t)

    def get_chemical_from_data(self, node: BaseEntity) -> Optional[Chemical]:
        namespace = node.get(NAMESPACE)

        if namespace.lower() not in {'chebi', 'chebiid'}:
            return

        identifier = node.get(IDENTIFIER)
        name = node.get(NAME)

        if namespace.lower() == 'chebi':
            if identifier is not None:
                return self.get_chemical_by_chebi_id(identifier)

            if name is not None:
                return self.get_chemical_by_chebi_name(name)

            else:
                raise ValueError

        elif namespace.lower() == 'chebiid':
            return self.get_chemical_by_chebi_id(name)

    def enrich_chemical_hierarchy(self, graph: BELGraph) -> None:
        """Enrich the parents for all ChEBI chemicals in the graph."""
        for _, data in graph.nodes(data=True):
            chemical = self.get_chemical_from_data(data)

            if chemical is None:
                continue

            parent = chemical.parent
            while parent is not None:
                graph.add_is_a(chemical.as_bel(), parent.as_bel())
                chemical, parent = parent, parent.parent

    def _list_equivalencies(self) -> List[Chemical]:
        return self.session.query(Chemical).filter(Chemical.parent_id.isnot(None))

    def _iterate_relations(self):
        # return self.session.query(Relation).limit(100)
        return tqdm(self.list_relations(), total=self.count_relations(), desc='Relation')

    def to_bel(self) -> BELGraph:
        """Export BEL."""
        graph = BELGraph(
            name=_chebi_bel_name,
            version=_chebi_bel_version,
            description=_chebi_description,
        )

        namespace = self.upload_bel_namespace()  # Make sure the super id namespace is available
        graph.namespace_url[namespace.keyword] = namespace.url

        for relation in self._iterate_relations():
            relation.add_to_graph(graph)

        return graph

    def _create_namespace_entry_from_model(self, chemical: Chemical, namespace: Namespace) -> NamespaceEntry:
        """Create a namespace entry from a chemical model."""
        if chemical.name:
            return NamespaceEntry(
                encoding=chemical.bel_encoding,
                name=chemical.name,
                identifier=chemical.chebi_id,
                namespace=namespace,
            )

    @staticmethod
    def _get_identifier(chemical: Chemical) -> str:
        """Get the identifier from the chemical model."""
        return chemical.chebi_id

    @staticmethod
    def _get_name(chemical: Chemical) -> str:
        """Get the name of the chemical."""
        return chemical.safe_name

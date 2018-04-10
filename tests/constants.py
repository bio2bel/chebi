# -*- coding: utf-8 -*-

import logging
import os

from bio2bel.testing import make_temporary_cache_class_mixin
from bio2bel_chebi import Manager

log = logging.getLogger(__name__)

HERE = os.path.dirname(os.path.realpath(__file__))
resources_directory_path = os.path.join(HERE, 'resources')

inchis = os.path.join(resources_directory_path, 'chebiId_inchi.tsv')
compounds = os.path.join(resources_directory_path, 'compounds.tsv.gz')
relations = os.path.join(resources_directory_path, 'relation.tsv')

TemporaryCacheClsMixin = make_temporary_cache_class_mixin(Manager)


class PopulatedDatabaseMixin(TemporaryCacheClsMixin):
    @classmethod
    def populate(cls):
        cls.manager._load_inchis(url=inchis)
        cls.manager._populate_compounds(url=compounds)
        cls.manager._populate_relations(url=relations)

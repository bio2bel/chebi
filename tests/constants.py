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

target_ids = {
    3558,
    38545,
    32020,  # pitavastatin
    38561,  # fluvastatin
    87635,  # statin (synthetic)
    87631,  # statin
    35821,  # anticholesteremic drug
}


class PopulatedDatabaseMixin(TemporaryCacheClsMixin):
    @classmethod
    def populate(cls):
        Manager.populate(
            cls.manager,
            inchis_url=inchis,
            compounds_url=compounds,
            # relations_url=relations,
        )

# -*- coding: utf-8 -*-

from pybel.constants import NAMESPACE_DOMAIN_CHEMICAL
from pybel_tools.ols_utils import OlsNamespaceOntology

__all__ = [
    'MODULE_NAME',
    'MODULE_DOMAIN',
    'MODULE_FUNCTIONS',
    'write_belns',
    'deploy_to_arty',
]

MODULE_NAME = 'chebi'
MODULE_DOMAIN = NAMESPACE_DOMAIN_CHEMICAL
MODULE_FUNCTIONS = 'A'

ontology = OlsNamespaceOntology(MODULE_NAME, MODULE_DOMAIN, MODULE_FUNCTIONS)

write_belns = ontology.write
deploy_to_arty = ontology.deploy

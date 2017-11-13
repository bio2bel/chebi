# -*- coding: utf-8 -*-

from pybel.constants import NAMESPACE_DOMAIN_CHEMICAL
from pybel_tools.ols_utils import OlsNamespaceOntology

__all__ = [
    'MODULE_NAME',
    'MODULE_DOMAIN',
    'MODULE_ENCODING',
    'write_belns',
    'deploy_to_arty',
]

MODULE_NAME = 'chebi'
MODULE_DOMAIN = NAMESPACE_DOMAIN_CHEMICAL
MODULE_ENCODING = 'A'

ontology = OlsNamespaceOntology(MODULE_NAME, MODULE_DOMAIN, encoding=MODULE_ENCODING)

write_belns = ontology.write_namespace
deploy_to_arty = ontology.deploy_namespace

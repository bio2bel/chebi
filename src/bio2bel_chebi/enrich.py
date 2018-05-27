# -*- coding: utf-8 -*-

"""Enrichment functions for BEL Graphs."""

import logging

from pybel import to_database
from .manager import Manager

__all__ = [
    'enrich_chemical_hierarchy',
    'to_bel',
    'upload_bel'
]

log = logging.getLogger(__name__)


def enrich_chemical_hierarchy(graph, manager=None):
    """Enriches the biological processses in a BEL graph

    :type graph: pybel.BELGraph
    :type manager: Optional[bio2bel_chebi.Manager]
    """
    manager = manager or Manager()
    return manager.enrich_chemical_hierarchy(graph)


def to_bel(manager=None):
    """Creates a BEL graph from the Gene Ontology

    :type manager: Optional[bio2bel_chebi.Manager]
    """
    manager = manager or Manager()
    return manager.to_bel()


def upload_bel(manager=None, pybel_manager=None):
    """Creates a BEL graph from the Gene Ontology and uplopads it to the PyBEL edge store

    :type manager: Optional[bio2bel_chebi.Manager]
    :type pybel_manager: Optional[pybel.Manager]
    :rtype: pybel.manager.models.Network
    """
    log.info('converting bel')
    graph = to_bel(manager=manager)
    log.info('storing')
    return to_database(graph, connection=pybel_manager)

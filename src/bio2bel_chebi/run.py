# -*- coding: utf-8 -*-

from ols_client import get_labels
from pybel_tools.definition_utils import write_namespace
from pybel_tools.resources import deploy_namespace, get_today_arty_namespace

CHEBI_MODULE_NAME = 'chebi'


def deploy_to_arty():
    """Gets the data and writes BEL namespace file to artifactory"""
    values = get_labels('chebi')

    file_name = get_today_arty_namespace(CHEBI_MODULE_NAME)

    with open(file_name, 'w') as file:
        write_namespace(
            namespace_name="HGNC Gene Families",
            namespace_keyword="GFAM",
            namespace_domain="Gene and Gene Products",
            namespace_species='9606',
            namespace_description="HUGO Gene Nomenclature Committee (HGNC) curated gene families",
            citation_name='www.ebi.ac.uk/chebi/',
            author_name='Charles Tapley Hoyt',
            author_contact="charles.hoyt@scai.fraunhofer.de",
            author_copyright='Creative Commons by 4.0',
            values=values,
            functions="GRP",
            file=file
        )

    deploy_namespace(file_name, CHEBI_MODULE_NAME)


if __name__ == '__main__':
    deploy_to_arty()

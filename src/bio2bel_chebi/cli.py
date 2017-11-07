# -*- coding: utf-8 -*-

"""Run this script with either :code:`python3 -m bio2bel_chebi arty`"""

from __future__ import print_function

import logging
import sys

import click

from bio2bel_chebi.manager import Manager
from bio2bel_chebi.run import MODULE_DOMAIN, MODULE_FUNCTIONS, MODULE_NAME
from pybel_tools.ols_utils import OlsNamespaceOntology


@click.group()
def main():
    """ChEBI to BEL"""
    logging.basicConfig(level=10, format="%(asctime)s - %(levelname)s - %(message)s")


@main.command()
@click.option('-b', '--ols-base', help="Custom OLS base url")
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
def write(ols_base, output):
    """Writes BEL namespace"""
    ontology = OlsNamespaceOntology(MODULE_NAME, MODULE_DOMAIN, MODULE_FUNCTIONS, ols_base=ols_base)
    ontology.write(output)


@main.command()
@click.option('-b', '--ols-base', help="Custom OLS base url")
@click.option('--no-hash-check', is_flag=True)
def deploy(ols_base=None, no_hash_check=False):
    """Deploy to Artifactory"""
    ontology = OlsNamespaceOntology(MODULE_NAME, MODULE_DOMAIN, MODULE_FUNCTIONS, ols_base=ols_base)
    success = ontology.deploy(hash_check=(not no_hash_check))
    click.echo('Deployed to {}'.format(success) if success else 'Duplicate not deployed')


@main.command()
@click.option('-c', '--connection', help="Custom OLS base url")
def populate(connection):
    m = Manager(connection=connection)
    m.populate()


if __name__ == '__main__':
    main()

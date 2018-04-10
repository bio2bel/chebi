# -*- coding: utf-8 -*-

"""Run this script with :code:`python3 -m bio2bel_chebi`"""

import sys

import click

from bio2bel.cli_utils import build_cli
from pybel_tools.ols_utils import OlsNamespaceOntology
from .manager import Manager
from .run import MODULE_DOMAIN, MODULE_ENCODING, MODULE_NAME

main = build_cli(Manager)


@main.command()
@click.option('-b', '--ols-base', help="Custom OLS base url")
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
def write(ols_base, output):
    """Writes BEL namespace"""
    ontology = OlsNamespaceOntology(MODULE_NAME, MODULE_DOMAIN, encoding=MODULE_ENCODING, ols_base=ols_base)
    ontology.write_namespace(output)


@main.command()
@click.option('-b', '--ols-base', help="Custom OLS base url")
@click.option('--no-hash-check', is_flag=True)
def deploy(ols_base=None, no_hash_check=False):
    """Deploy the ChEBI namespace to Artifactory"""
    ontology = OlsNamespaceOntology(MODULE_NAME, MODULE_DOMAIN, encoding=MODULE_ENCODING, ols_base=ols_base)
    success = ontology.deploy_namespace(hash_check=(not no_hash_check))
    click.echo('Deployed to {}'.format(success) if success else 'Duplicate not deployed')


@main.command()
@click.pass_obj
def upload_bel_ids(manager):
    n = manager.upload_bel_ids()
    click.echo('uploaded {} {}'.format(n.id, n))


if __name__ == '__main__':
    main()

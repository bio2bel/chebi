# -*- coding: utf-8 -*-

"""Run this script with :code:`python3 -m bio2bel_chebi`"""

from __future__ import print_function

import click
import logging
import sys

from bio2bel_chebi.constants import DEFAULT_CACHE_CONNECTION
from bio2bel_chebi.manager import Manager
from bio2bel_chebi.run import MODULE_DOMAIN, MODULE_ENCODING, MODULE_NAME
from pybel_tools.ols_utils import OlsNamespaceOntology


@click.group()
@click.option('-c', '--connection', help='Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
@click.pass_context
def main(ctx, connection):
    """Convert ChEBI to BEL"""
    logging.basicConfig(level=10, format="%(asctime)s - %(levelname)s - %(message)s")
    ctx.obj = Manager(connection=connection)


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
def populate(manager):
    """Populates the database"""
    manager.populate()


@main.command()
@click.option('-y', '--yes', is_flag=True)
@click.pass_obj
def drop(manager, yes):
    """Drops database"""
    if yes or click.confirm('Drop everything?'):
        manager.drop_all()


@main.command()
@click.option('-v', '--debug', is_flag=True)
@click.option('-h', '--host')
@click.option('-p', '--port', type=int)
@click.pass_obj
def web(manager, debug, host, port):
    """Run the web app"""
    from .web import get_app
    app = get_app(connection=manager, url='/')
    app.run(debug=debug, host=host, port=port)


if __name__ == '__main__':
    main()

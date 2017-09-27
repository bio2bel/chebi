# -*- coding: utf-8 -*-

"""Run this script with either :code:`python3 -m bio2bel_chebi arty`"""

from __future__ import print_function

import logging

import click

from ols_client.api import OLS_BASE
from .run import deploy_to_arty


@click.group()
def main():
    """Output gene family hierarchy as BEL script and BEL namespace"""
    logging.basicConfig(level=10, format="%(asctime)s - %(levelname)s - %(message)s")


@main.command()
@click.option('-b', '--ols-base', help="OLS base url. Defaults to {}".format(OLS_BASE))
def deploy(ols_base):
    """Deploy to artifactory"""
    deploy_to_arty(ols_base=ols_base)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

"""Run this script with either :code:`python3 -m bio2bel_chebi arty`"""

from __future__ import print_function

import logging

import click

from .run import deploy_to_arty


@click.group()
def main():
    """Output gene family hierarchy as BEL script and BEL namespace"""
    logging.basicConfig(level=10, format="%(asctime)s - %(levelname)s - %(message)s")


@main.command()
def arty():
    """Deploy to artifactory"""
    deploy_to_arty()


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

import os

from bio2bel.utils import get_connection, get_data_dir

MODULE_NAME = 'chebi'
DATA_DIR = get_data_dir(MODULE_NAME)
DEFAULT_CACHE_CONNECTION = get_connection(MODULE_NAME)

COMPOUNDS_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/compounds.tsv.gz'
NAMES_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/names.tsv.gz'
ACCESSION_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/database_accession.tsv'
INCHIS_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/chebiId_inchi.tsv'
RELATIONS_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/relation.tsv'

COMPOUNDS_DATA_PATH = os.path.join(DATA_DIR, 'compounds.tsv.gz')
NAMES_DATA_PATH = os.path.join(DATA_DIR, 'names.tsv.gz')
ACCESSION_DATA_PATH = os.path.join(DATA_DIR, 'database_accession.tsv')
INCHIS_DATA_PATH = os.path.join(DATA_DIR, 'chebiId_inchi.tsv')
RELATIONS_DATA_PATH = os.path.join(DATA_DIR, 'relation.tsv')

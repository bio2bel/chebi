# -*- coding: utf-8 -*-

COMPOUNDS_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/compounds.tsv.gz'
NAMES_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/names.tsv.gz'
ACCESSION_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/database_accession.tsv'
INCHIS_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/chebiId_inchi.tsv'

from os import environ, makedirs, path

#: The default directory where PyBEL files, including logs and the  default cache, are stored. Created if not exists.
DATA_DIR = environ.get('CHEBI_RESOURCE_DIRECTORY', path.join(path.expanduser('~'), '.pybel', 'bio2bel', 'chebi'))
makedirs(DATA_DIR, exist_ok=True)

DEFAULT_CACHE_NAME = 'chebi.db'
DEFAULT_CACHE_LOCATION = path.join(DATA_DIR, DEFAULT_CACHE_NAME)
DEFAULT_CACHE_CONNECTION = 'sqlite:///' + DEFAULT_CACHE_LOCATION

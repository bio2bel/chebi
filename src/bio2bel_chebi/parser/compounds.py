# -*- coding: utf-8 -*-

import logging
import os
from urllib.request import urlretrieve

import pandas as pd

from ..constants import COMPOUNDS_DATA_PATH, COMPOUNDS_URL

log = logging.getLogger(__name__)


def download_compounds(force_download=False):
    """Downloads the compounds information

    :param bool force_download: If true, overwrites a previously cached file
    :rtype: str
    """
    if os.path.exists(COMPOUNDS_DATA_PATH) and not force_download:
        log.info('using cached data at %s', COMPOUNDS_DATA_PATH)
    else:
        log.info('downloading %s to %s', COMPOUNDS_URL, COMPOUNDS_DATA_PATH)
        urlretrieve(COMPOUNDS_URL, COMPOUNDS_DATA_PATH)

    return COMPOUNDS_DATA_PATH


def get_compounds_df(url=None, cache=True, force_download=False):
    """Gets the ChEBI accession flat file.

    This file contains the columns: ID, STATUS, CHEBI_ACCESSION, PARENT_ID, NAME, DEFINITION

    :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
    :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
    :param bool force_download: If true, overwrites a previously cached file
    :rtype: pandas.DataFrame
    """
    if url is None and cache:
        url = download_compounds(force_download=force_download)

    return pd.read_csv(
        url or COMPOUNDS_URL,
        sep='\t',
        compression='gzip',
        na_values=['null'],
        low_memory=False
    )

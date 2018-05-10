# -*- coding: utf-8 -*-

import logging
import os
from urllib.request import urlretrieve

import pandas as pd

from ..constants import ACCESSION_DATA_PATH, ACCESSION_URL

log = logging.getLogger(__name__)


def download_accessions(force_download=False):
    """Downloads the compound accessions

    :param bool force_download: If true, overwrites a previously cached file
    :rtype: str
    """
    if os.path.exists(ACCESSION_DATA_PATH) and not force_download:
        log.info('using cached data at %s', ACCESSION_DATA_PATH)
    else:
        log.info('downloading %s to %s', ACCESSION_URL, ACCESSION_DATA_PATH)
        urlretrieve(ACCESSION_URL, ACCESSION_DATA_PATH)

    return ACCESSION_DATA_PATH


def get_accession_df(url=None, cache=True, force_download=False):
    """Gets the ChEBI accession flat file.

    This file contains five columns: ID, COMPOUND_ID, SOURCE, TYPE, and ACCESSION_NUMBER

    :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
    :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
    :param bool force_download: If true, overwrites a previously cached file
    :rtype: pandas.DataFrame
    """
    if url is None and cache:
        url = download_accessions(force_download=force_download)

    return pd.read_csv(
        url or ACCESSION_URL,
        sep='\t'
    )

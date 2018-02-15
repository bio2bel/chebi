# -*- coding: utf-8 -*-


import logging
import os
from urllib.request import urlretrieve

import pandas as pd

from ..constants import NAMES_DATA_PATH, NAMES_URL

log = logging.getLogger(__name__)


def download_names(force_download=False):
    """Downloads the compound names

    :param bool force_download: If true, overwrites a previously cached file
    :rtype: str
    """
    if os.path.exists(NAMES_DATA_PATH) and not force_download:
        log.info('using cached data at %s', NAMES_DATA_PATH)
    else:
        log.info('downloading %s to %s', NAMES_URL, NAMES_DATA_PATH)
        urlretrieve(NAMES_URL, NAMES_DATA_PATH)

    return NAMES_DATA_PATH


def get_names_df(url=None, cache=True, force_download=False):
    """Gets the ChEBI names flat file.

    This file contains five columns: ID, COMPOUND_ID, TYPE, SOURCE, NAME, ADAPTED, and LANGUAGE

    :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
    :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
    :param bool force_download: If true, overwrites a previously cached file
    :rtype: pandas.DataFrame
    """
    if url is None and cache:
        url = download_names(force_download=force_download)

    return pd.read_csv(
        url or NAMES_URL,
        sep='\t',
        compression='gzip'
    )

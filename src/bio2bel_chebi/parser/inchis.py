# -*- coding: utf-8 -*-


import logging
import os
from urllib.request import urlretrieve

import pandas as pd

from ..constants import INCHIS_DATA_PATH, INCHIS_URL

log = logging.getLogger(__name__)


def download_inchis(force_download=False):
    """Downloads the compound inchis

    :param bool force_download: If true, overwrites a previously cached file
    :rtype: str
    """
    if os.path.exists(INCHIS_DATA_PATH) and not force_download:
        log.info('using cached data at %s', INCHIS_DATA_PATH)
    else:
        log.info('downloading %s to %s', INCHIS_URL, INCHIS_DATA_PATH)
        urlretrieve(INCHIS_URL, INCHIS_DATA_PATH)

    return INCHIS_DATA_PATH


def get_inchis_df(url=None, cache=True, force_download=False):
    """Gets the compound's inchi keys

    :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
    :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
    :param bool force_download: If true, overwrites a previously cached file
    :rtype: pandas.DataFrame
    """
    if url is None and cache:
        url = download_inchis(force_download=force_download)

    return pd.read_csv(
        url or INCHIS_URL,
        sep='\t'
    )

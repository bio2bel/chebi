# -*- coding: utf-8 -*-


import logging
import os
from urllib.request import urlretrieve

import pandas as pd

from ..constants import RELATIONS_DATA_PATH, RELATIONS_URL

log = logging.getLogger(__name__)


def download_relations(force_download=False):
    """Downloads the compound relations

    :param bool force_download: If true, overwrites a previously cached file
    :rtype: str
    """
    if os.path.exists(RELATIONS_DATA_PATH) and not force_download:
        log.info('using cached data at %s', RELATIONS_DATA_PATH)
    else:
        log.info('downloading %s to %s', RELATIONS_URL, RELATIONS_DATA_PATH)
        urlretrieve(RELATIONS_URL, RELATIONS_DATA_PATH)

    return RELATIONS_DATA_PATH


def get_relations_df(url=None, cache=True, force_download=False):
    """Gets the ChEBI relations flat file

    Columns are: ID, TYPE, INIT_ID, FINAL_ID, STATUS

    :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
    :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
    :param bool force_download: If true, overwrites a previously cached file
    :rtype: pandas.DataFrame
    """
    if url is None and cache:
        url = download_relations(force_download=force_download)

    return pd.read_csv(
        url or RELATIONS_URL,
        sep='\t',
    )

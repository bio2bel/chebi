# -*- coding: utf-8 -*-

import pandas as pd

from bio2bel_chebi.constants import NAMES_URL


def get_names_df(url=None):
    """Gets the ChEBI names flat file.

    This file contains five columns: ID, COMPOUND_ID, TYPE, SOURCE, NAME, ADAPTED, and LANGUAGE

    :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
    :rtype: pandas.DataFrame
    """
    return pd.read_csv(
        url or NAMES_URL,
        sep='\t',
        compression='gzip'
    )

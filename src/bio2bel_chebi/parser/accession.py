# -*- coding: utf-8 -*-

import pandas as pd

from bio2bel_chebi.constants import ACCESSION_URL


def get_accession_df(url=None):
    """Gets the ChEBI accession flat file.

    This file contains five columns: ID, COMPOUND_ID, SOURCE, TYPE, and ACCESSION_NUMBER

    :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
    :rtype: pandas.DataFrame
    """
    return pd.read_csv(
        url or ACCESSION_URL,
        sep='\t'
    )

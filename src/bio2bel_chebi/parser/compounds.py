# -*- coding: utf-8 -*-

import pandas as pd

from bio2bel_chebi.constants import COMPOUNDS_URL


def get_compounds_df(url=None):
    """Gets the ChEBI accession flat file.

    This file contains the columns: ID, STATUS, CHEBI_ACCESSION, PARENT_ID, NAME, DEFINITION

    :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
    :rtype: pandas.DataFrame
    """
    return pd.read_csv(
        url or COMPOUNDS_URL,
        sep='\t',
        compression='gzip',
        na_values=['null'],
        low_memory=False
    )

import pandas as pd

from bio2bel_chebi.constants import INCHIS_URL

def get_inchis_df(url=None):
    """

    :param url:
    :return:
    """
    return pd.read_csv(
        url or INCHIS_URL,
        sep='\t'
    )
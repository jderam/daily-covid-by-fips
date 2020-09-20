from datetime import datetime
import pandas as pd
from typing import Dict


def fips_lookup(f: str, d: datetime, df: pd.DataFrame) -> Dict[str, int]:
    """ Look up any FIPS + Date combination
    Args:
        f: 5-digit FIPS code in string format
        d: Date to lookup numbers for
    Returns:
        results: Dictionary containing the following counts
            daily cases
            cumulative_cases
            daily_deaths
            cumulative_deaths
            population
    """
    results = {}
    temp_df = df[(df["fips"] == f) & (df["date"] == d)]
    row_count = len(temp_df)
    if row_count == 0:
        return results
    else:
        temp_df = temp_df.set_index("fips")
        temp_df = temp_df.drop(columns="date")
        results = temp_df.T.to_dict()[f]
        return results

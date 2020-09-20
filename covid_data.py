import numpy as np
import pandas as pd
from typing import List, Dict


pop_file = "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv"
nyt_file = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
out_file = "data/nyt_enriched.pkl"


def fips_populations(file_name: str = pop_file, raw: bool = False) -> pd.DataFrame:
    """ Read census population data, process, and return as DataFrame
    Args:
        file_name: Path or URL to source csv file.
        raw: If True, return the dataframe before applying transformations.
            Useful for troubleshooting purposes.
    Returns:
        pop_df: Population data by FIPS code.
    """
    pop_dtypes: Dict[str, str] = {
        "SUMLEV": "str",
        "STATE": "str",
        "COUNTY": "str",
    }
    pop_df = pd.read_csv(file_name, dtype=pop_dtypes, encoding="ISO-8859-1")
    if raw:
        return pop_df
    pop_df = pop_df[pop_df['SUMLEV'] == "050"]

    select_cols: List[str] = [
        'STATE',
        'COUNTY',
        'STNAME',
        'CTYNAME',
        'POPESTIMATE2019',
    ]
    pop_df = pop_df[select_cols]

    pop_df['FIPS_CODE'] = pop_df['STATE'] + pop_df['COUNTY']

    total_rows: int = len(pop_df)
    unique_fips: int = len(pop_df.FIPS_CODE.unique())
    assert total_rows == unique_fips, \
        f"Total rows ({total_rows}) and unique FIPS_CODE counts ({unique_fips}) do not match"
    return pop_df


def nyt_covid_data(file_name: str = nyt_file, raw: bool = False) -> pd.DataFrame:
    """ Read NYT COVID-19 data, process, and return as DataFrame
    Args:
        file_name: Path or URL to source csv file.
        raw: If True, return the dataframe before applying transformations.
            Useful for troubleshooting purposes.
    Returns:
        nyt_df: COVID-19 cases and deaths by FIPS+date
    """
    nyt_dtypes: Dict[str, str] = {
        "fips": "str",
    }
    nyt_df = pd.read_csv(file_name, dtype=nyt_dtypes, parse_dates=["date"])
    if raw:
        return nyt_df
    nyt_df = nyt_df[~nyt_df['fips'].isnull()]
    nyt_df.sort_values(by=["fips", "date"], inplace=True, ignore_index=True)
    nyt_df["new_fips"] = nyt_df["fips"].ne(nyt_df["fips"].shift())
    nyt_df["daily_cases"] = np.where(nyt_df["new_fips"] == True,
                                     nyt_df["cases"],
                                     nyt_df["cases"] - nyt_df["cases"].shift()).astype('int')
    nyt_df["daily_deaths"] = np.where(nyt_df["new_fips"] == True,
                                      nyt_df["deaths"],
                                      nyt_df["deaths"] - nyt_df["deaths"].shift()).astype('int')
    total_rows = len(nyt_df)
    composite_key = nyt_df["date"].astype("str") + nyt_df["fips"]
    unique_date_plus_fips = len(composite_key.unique())
    assert total_rows == unique_date_plus_fips, \
        f"Total rows ({total_rows}) and unique date+fips counts ({unique_date_plus_fips}) do not match"
    return nyt_df


def cleanup_output(nyt_enriched_df: pd.DataFrame) -> pd.DataFrame:
    """ Drop extraneous columns and rename columns for sake of consistency.
    Args:
        nyt_enriched_df: Merged DataFrame
    Returns:
        nyt_enriched_df: Cleaned-up version of input DataFrame
    """
    col_map = {
        "fips": "fips",
        "date": "date",
        "daily_cases": "daily_cases",
        "cases": "cumulative_cases",
        "daily_deaths": "daily_deaths",
        "deaths": "cumulative_deaths",
        "POPESTIMATE2019": "population",
    }
    nyt_enriched_df = nyt_enriched_df[col_map.keys()].rename(columns=col_map)
    return nyt_enriched_df


if __name__ == "__main__":
    pop_df = fips_populations()
    nyt_df = nyt_covid_data()
    nyt_enriched_df = nyt_df.merge(pop_df,
                                   how="inner",
                                   left_on="fips",
                                   right_on="FIPS_CODE")
    nyt_enriched_df = cleanup_output(nyt_enriched_df)
    nyt_enriched_df.to_pickle(out_file, compression="bz2")


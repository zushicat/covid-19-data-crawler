import os
from typing import Any, Dict, List

import pandas as pd

DIRNAME = os.path.dirname(__file__)
DF_NATIONS = pd.read_csv(f"{DIRNAME}/data/wikidata_nations_data.csv", delimiter=";")
DF_DISTRICTS = pd.read_csv(f"{DIRNAME}/data/wikidata_community_data.csv", delimiter=";")

def get_national_data(df: pd.DataFrame) -> pd.DataFrame:
    df = pd.merge(df, DF_NATIONS[["countryCode", "country_name_german", "population_density"]], on="countryCode",how='left')
    df = df.dropna(how='any', axis=0)  # drop row if None is in any column value (then it's most likely not found in list)
    df.drop_duplicates(subset=["reportDate", "countryCode"], keep="first", inplace=True) # if > 1 names with equal stateCode in list
    df["population_density"] = df["population_density"].astype(int)
    
    return df


def get_district_data(df: pd.DataFrame) -> pd.DataFrame:
    DF_DISTRICTS["ags"] = DF_DISTRICTS["ags"].astype(int)
    df["ags"] = df["ags"].astype(int)
    
    df = pd.merge(df, DF_DISTRICTS[["ags", "population_density", "community_nam"]], on="ags",how='left')
    df = df.dropna(how='any', axis=0)
    df["population_density"] = df["population_density"].astype(int)

    df = df.rename(columns={"community_nam": "district_name"})
    
    return df
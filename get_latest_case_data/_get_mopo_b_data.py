'''
Berliner Morgenpost is doing a great job of collecting data on different levels:
- 0: nation level (international)
- 1: state level
- 2: district level

Data url:
https://funkeinteraktiv.b-cdn.net/history.v4.csv

The respective original sources can also be found in the csv file (which I drop here for practicality).

Interactive usage of this data:
https://interaktiv.morgenpost.de/corona-virus-karte-infektionen-deutschland-weltweit/
'''

#import csv
import datetime
import io
import json
import os
import requests
from typing import Tuple

from ._by_date import get_date
from .get_location_data._enrich_mopo_b_data import get_district_data, get_national_data

import pandas as pd


DIRNAME = os.path.dirname(__file__)
DATA_URL = "https://funkeinteraktiv.b-cdn.net/history.v4.csv"

def get_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    r = requests.get(DATA_URL)
    r.encoding = 'utf-8'
    r = r.text
    df = pd.read_csv(io.StringIO(r))

    df.drop([
        "parent", "label", "label_parent", "label_parent_en", "lat", "lon", "updated", "retrieved", "source", "source_url", "scraper"
    ], axis=1, inplace=True) 

    df = df.dropna(how='any', axis=0)  # drop row if None is in any column value
    df = df[df["population"].notna()]
    df["population"] = df["population"].astype(int)

    df["date"] = pd.to_datetime(df["date"], format='%Y%m%d')  # str to date
    df["levels"] = df.apply(lambda x: int(x["levels"].split(",")[0]) if isinstance(x["levels"], str) else x["levels"], axis=1)  # get level from level list: last 1-digit number
    
    df['id'] = df['id'].str.upper()  # ids to upper case
    
    df_n = df.loc[df["levels"] == 0]  # nations level (international)
    df_s = df.loc[df["levels"] == 1]  # state level
    df_d = df.loc[df["levels"] == 2]  # district level

    df_n = df_n.rename(columns={"id": "countryCode", "label_en": "country_name_en"})
    df_s = df_s.rename(columns={"label_en": "state_name_en"})
    df_d = df_d.drop(["label_en"], axis=1)
    
    df_list = [df_n, df_s, df_d]
    for i, _ in enumerate(df_list):
        df_list[i] = df_list[i].drop(["levels"], axis=1)
        df_list[i] = df_list[i].rename(columns={"confirmed": "cases", "date": "reportDate", "population": "population_number"})
    
    return tuple(df_list) # df_n, df_s, df_d

    
def get_mopo_b_data()->None:
    df_n, df_s, df_d = get_data()

    today = get_date()

    # ***
    # nations level
    df_n = get_national_data(df_n)
    df_n.to_csv(f"{DIRNAME}/../data/{today}/nations_mopo_b.csv", index=False)
    
    # ***
    # state level of different nations:
    df_s[["countryCode", "stateCode"]] = df_s["id"].str.split(".",expand=True)
    df_s["stateCode"] = df_s[['countryCode', 'stateCode']].agg('-'.join, axis=1)
    df_s = df_s.drop(["id"], axis=1)

    df_states_by_nations = df_s.groupby('countryCode')
    for countryCode, grouf_df in df_states_by_nations:
        grouf_df.to_csv(f"{DIRNAME}/../data/{today}/states_{countryCode}_mopo_b.csv", index=False)

    # ***
    # district level
    df_d[["countryCode", "stateCode", "ags"]] = df_d["id"].str.split(".",expand=True)
    df_d["stateCode"] = df_d[['countryCode', 'stateCode']].agg('-'.join, axis=1)
    df_d = df_d.drop(["id"], axis=1)
    df_d = get_district_data(df_d)

    df_d.to_csv(f"{DIRNAME}/../data/{today}/communities_germany_mopo_b.csv", index=False)

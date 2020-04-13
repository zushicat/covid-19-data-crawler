import datetime
import os
from typing import List

from get_latest_case_data._by_date import get_date

import pandas as pd


DIRNAME = os.path.dirname(__file__)

def merge_data(csv_rki: str, csv_ts: str) -> pd.DataFrame:
    # ***
    # get RKI data
    cols = [
        "reportDate",
        "stateCode",
        "ags",
        "community_name",
        "cases",
        "recovered",
        "deaths",
        "population_number",
        "population_density"
    ]
    
    df = pd.read_csv(csv_rki, delimiter=",", usecols=cols)
    df["reportDate"] = pd.to_datetime(df["reportDate"], format='%d-%m-%Y')  # covert str to date
    
    # ***
    # make lookup table for communities and delete from data
    df_ags_lookup = df[["ags", "community_name", "stateCode", "population_number", "population_density"]].drop_duplicates()
    df_ags_lookup.set_index("ags", inplace=True)
    
    df.drop(["stateCode", "community_name", "population_number", "population_density"], axis=1, inplace=True) 
    df["source"] = "RKI"
    
    # ***
    # get Tagesspiegel data
    cols = [
        "reportDate",
        "ags",
        "cases",
        "recovered",
        "deaths"
    ]
    df_ts = pd.read_csv(csv_ts, delimiter=",", usecols=cols)
    df_ts["reportDate"] = pd.to_datetime(df_ts["reportDate"], format='%d-%m-%Y')  # covert str to date
    df_ts = df_ts.dropna(how='any',axis=0)  # drop row if None is in any column value
    
    df_ts["source"]= "Tagesspiegel"
    
    # ***
    # merge rki and ts data
    df = pd.merge(df, df_ts, on=["ags", "reportDate"], how='left', suffixes=('','_ts'))
    
    for data_case in ["cases", "deaths", "recovered"]:
        df[data_case] = df.apply(
            lambda x: x[f"{data_case}_ts"] 
            if pd.notna(x[f"{data_case}_ts"]) is True 
            else x[data_case], axis=1
        )
        df.drop(f"{data_case}_ts", axis=1, inplace=True)  
    
    df["source"] = df.apply(
            lambda x: x["source_ts"] 
            if pd.notna(x["source_ts"]) is True 
            else x["source"], axis=1
        )
    df.drop("source_ts", axis=1, inplace=True)  
    
    # ***
    # add missing rows from ts data to data
    df_ts = df_ts[~df_ts["reportDate"].isin(df["reportDate"])].dropna()
    df = pd.concat([df, df_ts], sort=False)
    df.sort_values(by=["ags","reportDate"])
    
    # ***
    # add locatity data to all rows based on ags
    df = pd.merge(
        df, df_ags_lookup[
            ["stateCode", "community_name", "population_number", "population_density"]
        ], on="ags", how="left"
    ).dropna()
    
    return df


def merge_accumulate_rki_ts(data_subdir_list: List[str]) -> None:
    data_subdir_list.remove(".DS_Store")
    data_subdir_list.sort(key=lambda x: datetime.datetime.strptime(x, "%d-%m-%Y"))
    
    latest_date = data_subdir_list[-1]
    csv_rki = f"{DIRNAME}/../data/{latest_date}/communities_germany_rki.csv"
    csv_ts = f"{DIRNAME}/../data/{latest_date}/communities_tagesspiegel.csv"
    
    df_communities = merge_data(csv_rki, csv_ts)
    # print(df_communities.loc[df_communities["ags"] == 5315])  # test plot cologne

    today = get_date()
    df_communities.to_csv(f"{DIRNAME}/../data/{today}/communities_germany_merged_rki_ts.csv", index=False)
    
    
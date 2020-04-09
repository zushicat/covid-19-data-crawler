'''
The newspaper Tagesspiegel basically uses Risklayer data (see links in README), although it seems that this is accumulated into their own
own spreadsheets. (Since I only have the spreadsheed id available, I nannot be sure where the data is actually coming from.)

See network requests in: https://interaktiv.tagesspiegel.de/lab/karte-sars-cov-2-in-deutschland-landkreise/
There are other spreadsheets requested which export data already covered by other sources, so those will be ignored.

Table name                              google spreadsheet ID
-----                                   -----
1 - cvLandkreiseRisklayer               2PACX-1vTiKkV3Iy-BsShsK3DSUeO9Gpen7VwsXM_haCOc8avj1PeoCIWqL4Os-Uza3jWMEUgmTrEizEV-Itq5
2 - cvLandkreiseRisklayerTote (a)       2PACX-1vRTkw2_oVkpZ9-WQk-BRf4Pgam9aRmH62uCUr9FiY0Uxv5ixtDhwSsecc_QMrfrD4ncHsCAua2f0TJh
3 - cvLandkreiseRisklayerGeheilte (b)   2PACX-1vRhIws1DYD51JuJJZbqSycONGWzvelHC6tAfH4RxGDcWHtP0AUYoErTlHXksWgwdddRyZkw8GdEHKZk

Accumulated numbers oncommunity level (incl. ags community key) of:
1 - overall cases (NOT infected only)
2 - deaths
3 - recovered


URL: https://docs.google.com/spreadsheets/d/e/<ID>/pub
Request URL (csv export): https://docs.google.com/spreadsheets/d/e/<ID>/pub?output=csv

Timeseries start at following dates, hence this data is only partially usefull: 
(a) 27.03.2020 - current
(b) 30.03.2020 - current
'''

import csv
import datetime
import io
import json
import os
import requests
from typing import Any, Dict, List

from ._by_date import get_date
from .get_location_data._enrich_tagesspiegel_data import get_ags_data

import pandas as pd


DIRNAME = os.path.dirname(__file__)
GOOGLESHEETS = {
    "cases": "2PACX-1vTiKkV3Iy-BsShsK3DSUeO9Gpen7VwsXM_haCOc8avj1PeoCIWqL4Os-Uza3jWMEUgmTrEizEV-Itq5",
    "deaths": "2PACX-1vRTkw2_oVkpZ9-WQk-BRf4Pgam9aRmH62uCUr9FiY0Uxv5ixtDhwSsecc_QMrfrD4ncHsCAua2f0TJh",
    "recovered": "2PACX-1vRhIws1DYD51JuJJZbqSycONGWzvelHC6tAfH4RxGDcWHtP0AUYoErTlHXksWgwdddRyZkw8GdEHKZk"
}

def change_date_format(date_str: str):
    return datetime.datetime.strptime(date_str, "%d.%m.%Y").strftime("%d-%m-%Y")


def make_rows(data: Dict[str, Any]) -> pd.DataFrame:
    '''
    From:
    {'community_name': 'Flensburg', 'dates': {'30-03-2020': {'cases': None, 'deaths': None, 'recovered': None}}}}
    To:
    [
        {"ags": 1001, "community_name": "Flensburg", "reportDate": "30-03-2020", "stateCode": ... ... } 
    ]
    '''
    flattened_data = []
    for ags, ags_data in data.items():
        population_data = get_ags_data(ags)
        for date, date_data in ags_data["dates"].items():
            tmp = {
                "reportDate": date,
                "ags": ags,
                "community_name": ags_data["community_name"]
            }
            tmp.update(population_data)
            for data_case, val in date_data.items():
                tmp[data_case] = val
            flattened_data.append(tmp)
    
    flattened_df = pd.DataFrame(flattened_data)

    # format population numbers to int
    for p_val in ["population_number", "population_density"]:
        flattened_df[p_val] = flattened_df[p_val].astype('Int64', errors='ignore')

    # get values per day
    for data_case in ["cases", "recovered", "deaths"]:
        flattened_df[data_case] = flattened_df[data_case].astype('Int64')
        flattened_df[f"{data_case}_day"] = flattened_df.groupby(['ags'])[data_case].diff()

    return flattened_df


def get_TS_communities_data() -> None:
    '''
    Get data and converts as followed:
    {
        <AGS>: 
        {
            community_name: <GEN>,
            dates:
            {
                <date>: {"cases": <int>, "recovered": null | <int>, "deaths": null | <int>}
            }
        }
    }
    Then flatten with each row in make_rows: values per date and per location -> export csv
    '''
    data: Dict[str, Any] = {}

    init_data = True
    for data_case, sheet_id in GOOGLESHEETS.items():
        url = f"https://docs.google.com/spreadsheets/d/e/{sheet_id}/pub?output=csv"
        r = requests.get(url)
        r.encoding = 'utf-8'
        r = r.text
        
        df = pd.read_csv(io.StringIO(r))
        df.drop(["current", "current_time"], axis=1, inplace=True) 
        try:
            df.drop(["ignore"], axis=1, inplace=True) 
        except:
            pass

        # ***
        #
        if init_data is True:
            data = {x[0]: {"community_name": x[1], "dates": {}} for x in df[["AGS", "GEN"]].values}
            init_data = False
        
        # ***
        #
        for ags in data.keys():
            df_current_row = df.loc[df['AGS'] == ags].copy()
            df_current_row.drop(["GEN", "AGS"], axis=1, inplace=True) 

            for col_name in df_current_row:
                formatted_date = change_date_format(col_name)
                try:
                    val = int(float(df_current_row[col_name].values[0]))
                except:
                    val = None
                
                if data[ags]["dates"].get(formatted_date) is None:
                    data[ags]["dates"][formatted_date] = {k: None for k in GOOGLESHEETS.keys()}
                data[ags]["dates"][formatted_date][data_case] = val

    flattened_df = make_rows(data)

    today = get_date()
    flattened_df.to_csv(f"{DIRNAME}/../data/{today}/communities_tagesspiegel.csv", index=False)

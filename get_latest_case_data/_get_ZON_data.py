'''
timeseries cities/communities (accumulated):
https://interactive.zeit.de/cronjobs/2020/corona/kreise-current.json -> city ids "ags" (gemeindeschluessel)
https://interactive.zeit.de/cronjobs/2020/corona/kreise-chronology.json -> data by id

timeseries international (accumulated):
https://interactive.zeit.de/cronjobs/2020/corona/international-chronoloy.json -> no ISO code, but attr. "land"

(only snapshot of current date) states (accumulated):
https://interactive.zeit.de/cronjobs/2020/corona/bundeslaender-current.json
'''

import csv
import datetime
import os
import requests
from typing import Any, List, Dict

from ._by_date import get_date
from .get_location_data._enrich_ZON_data import enrich_ZON_communities, enrich_ZON_nations

DIRNAME = os.path.dirname(__file__)

def _get_date_list(start_date: str, end_date:str) -> List[str]:
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    # end_date = datetime.datetime.strptime(end_date.split("T")[0], "%Y-%m-%d")  # if end_date == lastUpdate

    date_list: List[str] = []

    date_delta = end_date - start_date
    for i in range(date_delta.days + 1):
        current_date = start_date + datetime.timedelta(days=i)
        date_list.append(current_date.strftime('%d-%m-%Y'))

    return date_list


def _write_scv(data_in: List[Dict[str, Any]], file_name: str) -> None:
    today = get_date()
    field_names: List[str] = data_in[0].keys()
    with open(f"{DIRNAME}/../data/{today}/{file_name}.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=field_names, delimiter=";")
        writer.writeheader()
        writer.writerows(data_in)


def get_ZON_international_data() -> None:
    url = "https://interactive.zeit.de/cronjobs/2020/corona/international-chronoloy.json"
    r = requests.get(url)
    r = r.json()

    date_list: List[str] = _get_date_list(r["firstDate"], r["lastDate"])
    country_data_by_date: List[Dict[str, Any]]  = []   # int, str or maybe even None

    for country_data in r["laender"]:
        for i, current_date in enumerate(date_list):
            tmp: Dict[str, Any] = {
                "reportDate": current_date,
                "country_name_german": country_data["land"],
                "cases": country_data["counts"][i],
                "deaths": country_data["deaths"][i]
            }
            country_data_by_date.append(tmp)

    country_data_by_date = enrich_ZON_nations(country_data_by_date)
    _write_scv(country_data_by_date, "nations_ZON")


def get_ZON_communities_data() -> None:
    url = "https://interactive.zeit.de/cronjobs/2020/corona/kreise-chronology.json"
    r = requests.get(url)
    r = r.json()

    date_list: List[str] = _get_date_list(r["firstDate"], r["lastDate"])
    community_data_by_date: List[Dict[str, Any]]  = []   # int, str or maybe even None

    for community_data in r["kreise"]:
        for i, current_date in enumerate(date_list):
            tmp: Dict[str, Any] = {
                "reportDate": current_date,
                "ags": community_data["ags"],
                "cases": community_data["counts"][i],
            }
            community_data_by_date.append(tmp)
    
    community_data_by_date = enrich_ZON_communities(community_data_by_date)
    _write_scv(community_data_by_date, "communities_ZON")
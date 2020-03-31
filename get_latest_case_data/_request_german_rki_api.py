'''
Request API of Robert-Koch Institute for latest infections/deaths on state/local level

For further API information, see:
https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0/geoservice
(Dataset: https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0)

This is the underlaying data for their dashboard which you can find here:
https://experience.arcgis.com/experience/478220a4c454480e823b17327b2bf1d4
'''


from datetime import datetime
import csv
import os
import requests
from typing import Any, Dict, List

from ._accumulate_german_rki_numbers import enrich_data
from ._by_date import get_date
from .get_location_data._enrich_rki_data import enrich_with_population_data


DIRNAME = os.path.dirname(__file__)

STATE_IDS: Dict[str, str] = {
    "8": "Baden-Württemberg",
    "9": "Bavaria",
    "11": "Berlin",
    "12": "Brandenburg",
    "4": "Bremen",
    "2": "Hamburg",
    "6": "Hesse",
    "13": "Mecklenburg-Western Pomerania",
    "3": "Lower Saxony",
    "5": "North Rhine-Westphalia",
    "7": "Rhineland-Palatinate",
    "10": "Saarland",
    "14": "Saxony",
    "15": "Saxony-Anhalt",
    "1": "Schleswig-Holstein",
    "16": "Thuringia"
}

STATE_CODES: Dict[str, str] = {  # iso state code as use in script request_german-news_outlets.py
    "DE-BW": "Baden-Württemberg",
    "DE-BY": "Bavaria",
    "DE-BE": "Berlin",
    "DE-BB": "Brandenburg",
    "DE-HB": "Bremen",
    "DE-HH": "Hamburg",
    "DE-HE": "Hesse",
    "DE-MV": "Mecklenburg-Western Pomerania",
    "DE-NI": "Lower Saxony",
    "DE-NW": "North Rhine-Westphalia",
    "DE-RP": "Rhineland-Palatinate",
    "DE-SL": "Saarland",
    "DE-SN": "Saxony",
    "DE-ST": "Saxony-Anhalt",
    "DE-SH": "Schleswig-Holstein",
    "DE-TH": "Thuringia"
}
STATE_CODES = {v: k for k, v in STATE_CODES.items()}  # swap key, value


def get_date_from_timestamp(timestamp: int) -> str:
    timestamp /= 1000  # unit conversion
    date_format = "%d-%m-%Y"
    return datetime.fromtimestamp(timestamp).strftime(date_format)


def request_rki_api():
    community_numbers: List[Dict[str, Any]] = []

    for state_id in STATE_IDS.keys():
        '''
        Returns (data of attr. "features"): 
        [
            {
                'attributes': 
                {
                    'AnzahlFall': 1, 'AnzahlTodesfall': 0, 'Meldedatum': 1584144000000, 'IdLandkreis': '08111', 'IdBundesland': 8, 'Landkreis': 'SK Stuttgart'}
                }
        ]

        - Add state iso code
        - Add human readable date (from timestamp), format y-m-d i.e. 2020-03-18
        '''
        state_code: str = STATE_CODES[STATE_IDS[state_id]]
        url = f"https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/query?where=IdBundesland={state_id}&outFields=AnzahlFall,AnzahlTodesfall,Meldedatum,IdLandkreis,IdBundesland,Landkreis&outSR=4326&f=json"
        r = requests.get(url)
        lines = r.json()["features"]

        for line in lines:
            line: Dict[str, str] = line["attributes"]
            line["stateCode"]: str = state_code
            timestamp_report: int = line["Meldedatum"]
            line["reportDate"]: str = get_date_from_timestamp(timestamp_report)

            line["source"]: str = "RKI"

            # ***
            # normalize attribute naming
            del line["IdBundesland"]
            
            for key_old, key_new in {
                "AnzahlFall": "cases_day", 
                "AnzahlTodesfall": "deaths_day", 
                "Meldedatum": "reportDate_timestamp", 
                "IdLandkreis": "ags", 
                "Landkreis": "community_name"
            }.items():
                line[key_new] = line[key_old]
                del line[key_old]

            community_numbers.append(line)


    accumulated_communities = enrich_data(community_numbers)
    accumulated_communities = enrich_with_population_data(accumulated_communities)

    today = get_date()
    field_names: List[str] = accumulated_communities[0].keys()
    with open(f"{DIRNAME}/../data/{today}/communities_germany_rki.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=field_names, delimiter=",")
        writer.writeheader()
        writer.writerows(accumulated_communities)

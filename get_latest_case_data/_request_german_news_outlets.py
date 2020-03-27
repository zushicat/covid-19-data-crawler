'''
Reuquest API to retrieve German numbers on national and state level aggregated by news outlets ZON and Morgenpost 
Underlying source: local/state public health agencies

For further API details, check out:
https://github.com/jgehrcke/covid-19-germany-gae
'''

import csv
import json
import os
import requests
from typing import Any, Dict, List, Tuple

from ._by_date import get_date
from .get_location_data._enrich_outlets_data import enrich_with_population_data


DIRNAME = os.path.dirname(__file__)

STATE_CODES: Dict[str, str] = {
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

METRICS: List[str] = [
    "cases",
    "deaths"
]


def _change_date_format(date_str: str) -> str:  # i.e. 2020-03-18T23:00:00+01:00 -> y-m-d i.e.2020-03-18
    return date_str.split("T")[0]  # simply get rid of everything after T (no datetime needed here)


def _export_csv(state_numbers: Dict[str, Any], national_numbers: Dict[str, Any]) -> None:
    '''
    Both dicts need to be flattened for csv export.

    state_numbers in:
        {state: {"cases": {date; val, ...}, "deaths": {date: val, ...}}, ...}
    state_numbers out:
        [
           {"stateCode": <str>, "reportDate": <str>, "cases": <int>, "deaths": <int>}
        ]
    
    national_numbers in:
        {"cases":{date: val, ...}, "deaths": {date: val, ...}}
    national_numbers out:
        [
            {"stateCode": "DE-DE", "reportDate: <str>, "cases": <int>, "deaths": <int>}
        ]
    '''

    def write_csv(current_list: List[Dict[str, Any]], file_name: str) -> None:
        today = get_date()
        field_names: List[str] = current_list[0].keys()
        with open(f"{DIRNAME}/../data/{today}/{file_name}.csv", "w") as f:
            writer = csv.DictWriter(f, fieldnames=field_names, delimiter=",")
            writer.writeheader()
            writer.writerows(current_list)

    # ***
    # data for states:
    state_numbers_intermediate: Dict[str, Any] = {}  # -> {"reportDate": {"stateCode": {"cases": <int>, "deaths": <int>}}}
    for stateCode, metrics_vals in state_numbers.items():
        for metric, date_vals in metrics_vals.items():
            for reportDate, date_val in date_vals.items():
                if state_numbers_intermediate.get(reportDate) is None:
                    state_numbers_intermediate[reportDate]: Dict[str, Any] = {}
                if state_numbers_intermediate[reportDate].get(stateCode) is None:
                    state_numbers_intermediate[reportDate][stateCode]: Dict[str, int] = {}
                state_numbers_intermediate[reportDate][stateCode][metric] = date_val

    state_numbers_flattened: List[Dict[str, Any]] = []  # -> [{"stateCode": <str>, "reportDate": <str>, "cases": <int>, "deaths": <int}]
    for reportDate, stateCode_vals in state_numbers_intermediate.items():
        for stateCode, metrics_vals in stateCode_vals.items():
            tmp = {"stateCode": stateCode, "reportDate": reportDate}
            for metric, metric_val in metrics_vals.items():
                tmp[metric] = metric_val
            state_numbers_flattened.append(tmp)
    
    state_numbers_flattened = enrich_with_population_data(state_numbers_flattened)
    write_csv(state_numbers_flattened, "states_germany_news_api")

    # ***
    # national data:
    national_numbers_intermediate: Dict[str, Any] = {}
    for metric, date_vals in national_numbers.items():
        for reportDate, date_val in date_vals.items():
            if national_numbers_intermediate.get(reportDate) is None:
                national_numbers_intermediate[reportDate]: Dict[str, int] = {}
            national_numbers_intermediate[reportDate][metric]: int = date_val
    
    national_numbers_flattened: List[Dict[str, Any]] = []
    for reportDate, date_vals in national_numbers_intermediate.items():
        tmp = {"stateCode": "DE-DE", "reportDate": reportDate}
        for metric, metric_val in date_vals.items():
            tmp[metric] = metric_val
        national_numbers_flattened.append(tmp)
    
    national_numbers_flattened = enrich_with_population_data(national_numbers_flattened)
    write_csv(national_numbers_flattened, "national_germany_news_api")
    

def _request_data() -> Tuple:
    states_numbers: Dict[str, Any] = {}  # {state: {"cases": {date; val, ...}, "deaths": {date: val, ...}}, ...}
    national_numbers: Dict[str, Any] = {"cases": {}, "deaths": {}}  # {"cases":{date: val, ...}, "deaths": {date: val, ...}}

    for state_code in STATE_CODES.keys():
        for metric in METRICS:
            url = f"https://covid19-germany.appspot.com/timeseries/{state_code}/{metric}"
            r = requests.get(url)
            data_list: List[Dict[str, str]] = r.json()["data"]

            if states_numbers.get(state_code) is None:
                states_numbers[state_code] = {"cases": {}, "deaths": {}}

            for date_val in data_list:
                date: str
                num: int
                (date, num) = next(iter(date_val.items()))  # only one tuple in list
                date: str = _change_date_format(date)
                
                states_numbers[state_code][metric][date]: int = num  # save date -> int value per metric
                if national_numbers[metric].get(date) is None:
                    national_numbers[metric][date] = 0
                national_numbers[metric][date] += num

    return states_numbers, national_numbers


def request_news_outlet_api():
    state_numbers, national_numbers = _request_data()
    _export_csv(state_numbers, national_numbers)

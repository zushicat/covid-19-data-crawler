import csv
import json
import os
from typing import Any, Dict, List


DIRNAME = os.path.dirname(__file__)
STATE_CODES: Dict[str, str] = {  # iso state code as use in script request_german-news_outlets.py
    "DE-BW": "Baden-Württemberg",
    "DE-BY": "Bayern",
    "DE-BE": "Berlin",
    "DE-BB": "Brandenburg",
    "DE-HB": "Bremen",
    "DE-HH": "Hamburg",
    "DE-HE": "Hessen",
    "DE-MV": "Mecklenburg-Vorpommern",
    "DE-NI": "Niedersachsen",
    "DE-NW": "Nordrhein-Westfalen",
    "DE-RP": "Rheinland-Pfalz",
    "DE-SL": "Saarland",
    "DE-SN": "Sachsen",
    "DE-ST": "Sachsen-Anhalt",
    "DE-SH": "Schleswig-Holstein",
    "DE-TH": "Thüringen"
}
STATE_CODES = {v: k for k, v in STATE_CODES.items()}  # swap key, value


def _merge_dicts(x: Dict[str, Any], y: Dict[str, Any]) -> Dict[str, Any]:
        z = x.copy()   # start with x's keys and values
        z.update(y)    # modifies z with y's keys and values & returns None
        return z


def enrich_ZON_nations(data_in: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    nations_data: Dict[str, Any] = {}
    with open(f"{DIRNAME}/data/wikidata_nations_data.csv") as f:
        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            nations_data[line["country_name_german"]] = line
    
    enriched_data: List[Dict[str, Any]] = []
    for i, line in enumerate(data_in):
        if nations_data.get(line["country_name_german"]) is None:
            continue
        tmp = _merge_dicts(data_in[i], nations_data[line["country_name_german"]])
        enriched_data.append(tmp)
    
    return enriched_data

def enrich_ZON_communities(data_in: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    with open(f"{DIRNAME}/data/ZON_ags_key_data.json") as f:
        ZON_ags_key_data = json.load(f)

    with open(f"{DIRNAME}/data/wikidata_community_data.csv") as f:
        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            ags = str(int(line["ags"]))  # no leading 0 in ZON_ags_key_data.ags
            if ZON_ags_key_data.get(ags) is None:  # not in ZON list
                continue
            ZON_ags_key_data[ags]["population_density"] = line["population_density"]
    
    location_data: Dict[str, Any] = {}
    for ags, ags_data in ZON_ags_key_data.items():
        if ags_data.get("population_density") is None:  # not in ZON list
            continue
        location_data[ags] = {
            "ags": ags,
            "community_name": ags_data["name"],
            "state": ags_data["bundesland"],
            "stateCode": STATE_CODES[ags_data["bundesland"]],
            "population_number": ags_data["population"],
            "population_density": ags_data["population_density"],
            "lat": ags_data["lat"],
            "lng": ags_data["lon"]
        }
    
    for i, line in enumerate(data_in):
        if location_data.get(line["ags"]) is None:
            continue
        data_in[i] = _merge_dicts(data_in[i], location_data[line["ags"]])
    
    return data_in
    
    
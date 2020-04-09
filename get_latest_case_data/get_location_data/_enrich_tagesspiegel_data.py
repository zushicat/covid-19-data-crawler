import json
import os
from typing import Dict

import pandas as pd

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

DF = pd.read_csv(f"{DIRNAME}/data/wikidata_community_data.csv", delimiter=";")
DF["ags"] = DF["ags"].astype(int)

def get_ags_data(ags: int) -> Dict[str, int]:
    with open(f"{DIRNAME}/data/ZON_ags_key_data.json") as f:
        ZON_ags_key_data = json.load(f)
    
    try:
        ags_data = ZON_ags_key_data[str(ags)]
        stateCode = STATE_CODES[ags_data["bundesland"]]
    except:
        stateCode = None

    ags_df = DF.loc[DF["ags"] == ags]
    try:
        return {
            "population_number": ags_df["population_number"].values[0], 
            "population_density": ags_df["population_density"].values[0],
            "stateCode": stateCode
        }
    except:
        return {
            "population_number": None, 
            "population_density": None,
            "stateCode": stateCode
        }
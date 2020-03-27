import csv
import json
import os
from typing import Any, Dict, List


DIRNAME = os.path.dirname(__file__)


def _get_state_data() -> Dict[str, Dict[str, int]]:
    state_data: Dict[str, Dict[str, int]] = {}
    with open(f"{DIRNAME}/data/states_data.csv") as f:
        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            state_code = f'DE-{line["Kürzel"]}'
            state_data[state_code] = {
                "population_number": int(float(line["Einwohner (Mio.)[12]"].replace(",", ".")) * 1000000),
                "population_density": int(line["Einwohner je km²[12]"])
            }

    return state_data


def enrich_with_population_data(data_in: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    data_with_population: List[Dict[str, Any]] = []
    state_data = _get_state_data()

    for line in data_in:
        state_code = line["stateCode"]
        if state_data.get(state_code) is None:
            continue

        line["population_number"] = state_data[state_code]["population_number"]
        line["population_density"] = state_data[state_code]["population_density"]
       
        data_with_population.append(line)

    return data_with_population

import csv
import os
from typing import Any, Dict, List


DIRNAME = os.path.dirname(__file__)


def _load_district_data() -> Dict[str, Dict[str, int]]:
    district_data: Dict[str, Dict[str, int]] = {}

    with open(f"{DIRNAME}/data/landkreis_data.csv") as f:
        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            idx = line["KrS"]
            district_data[idx] = {
                "population_number": int(line["Einw."].replace(".", "")),
                "population_density": int(line["Bev.D.Ew./km²"])
        }
        return district_data


def _load_city_data() -> Dict[str, Dict[str, Dict[str, int]]]:
    with open(f"{DIRNAME}/data/kreisfreie_staedte_data.csv") as f:
        city_data: Dict[str, Dict[str, Dict[str, int]]] = {}

        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            name = (line["Stadt"].split("(")[0]).split("[")[0]  # "Aachen[1](50° 47′ N, 6° 5′ O)" -> "Aachen"
            name = " ".join(name.split())
            
            state_code = line["BL"].split()[-1]
            
            if state_code == "B":
                state_code = "BE"
            state_code = f"DE-{state_code}"

            if city_data.get(state_code) is None:
                city_data[state_code] = {}
            city_data[state_code][name] = {
                "population_number": int(line["EWjetzt"].split()[0].replace(".", "")),
                "population_density": int(line["Bev.-dichte(EW/km²)"])
            }
        return city_data


def _load_berlin_data() -> Dict[str, Dict[str, int]]:
    berlin_data: Dict[str, Dict[str, int]] = {}

    with open(f"{DIRNAME}/data/berlin_data.csv") as f:
        reader = csv.DictReader(f, delimiter=";")
        for line in reader:
            neighborhood = line["Bezirk"]
            berlin_data[neighborhood] = {
                "population_number": int(line["Einwohner[2](30. Juni 2019)"].replace(".", "")),
                "population_density": int(line["Einwohnerpro km²(30. Juni 2019)"].replace(".", ""))
            }
        return berlin_data


def _load_csv(request_date: str) -> List:
    with open(f"../get_latest_case_data/data/{request_date}/communities_germany_rki.csv") as f:
        reader = csv.DictReader(f, delimiter=";")
        return enrich_with_population_data(list(reader))


def enrich_with_population_data(data_in: List) -> List[Dict[str, Any]]:
    data_with_population: List[Dict[str, Any]] = []

    district_data = _load_district_data()
    city_data = _load_city_data()
    berlin_data = _load_berlin_data()
    

    for line in data_in:
        idx = line["IdLandkreis"]
        state_code = line["stateCode"]
        
        name = line["Landkreis"]
        name = name.split("(")[0]
        name = name.replace("i.d.", "in der ").replace("a.d.", "an der ").replace("i.", "im ")
        
        for repl in ["LK", "SK"]:
            name = name.replace(repl, "")
        name = " ".join(name.split())

        if district_data.get(idx) is None:
            if city_data[state_code].get(name) is None:
                if name.find("Berlin") != -1:
                    if berlin_data.get(name) is None:
                        continue
                    else:
                        line["population_number"] = berlin_data[name]["population_number"]
                        line["population_density"] = berlin_data[name]["population_density"]
                else:
                    continue
            else:
                line["population_number"] = city_data[state_code][name]["population_number"]
                line["population_density"] = city_data[state_code][name]["population_density"]
        else:
            line["population_number"] = district_data[idx]["population_number"]
            line["population_density"] = district_data[idx]["population_density"]

        data_with_population.append(line)
    
    return data_with_population


if __name__ == '__main__':
    data_with_population = _load_csv("27-03-2020")
    # field_names: List[str] = data_with_population[0].keys()
    # with open("../data/numbers_rki_germany_communities.csv", "w") as f:
    #     writer = csv.DictWriter(f, fieldnames=field_names, delimiter=";")
    #     writer.writeheader()
    #     writer.writerows(data_with_population)
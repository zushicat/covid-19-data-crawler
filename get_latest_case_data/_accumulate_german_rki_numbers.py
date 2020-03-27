'''
The RKI data per day reflects newly reported cases (per community), hence this accumulation script.
'''


import csv
import json
from typing import Any, Dict, List

from ._by_date import get_date


def _load_csv_data(request_date: str) -> Dict[str, Dict[str, Dict]]:
    '''
    Make dict: community -> timestamp -> data for community at timestamp
    '''
    with open(f"data/{request_date}/communities_germany_rki.csv") as f:
        reader = csv.DictReader(f, delimiter=";")
        # for line in list(reader):
        #     id_landkreis: int = line["IdLandkreis"]
        #     timestamp: int = int(line["Meldedatum"])
            
        #     if community_data.get(id_landkreis) is None:
        #         community_data[id_landkreis] = {}
        #     if community_data[id_landkreis].get(timestamp) is None:
        #         community_data[id_landkreis][timestamp] = line
        
        return enrich_data(list(reader))


def enrich_data(data_in: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    '''
    Make dict: community -> timestamp "Meldedatum" -> acc. data for community for consec. timestamp
    '''
    community_data: Dict[str, Dict[str, Dict]] = {}
    for line in data_in:
        id_landkreis: int = line["IdLandkreis"]
        timestamp: int = int(line["Meldedatum"])
        
        if community_data.get(id_landkreis) is None:
            community_data[id_landkreis] = {}
        if community_data[id_landkreis].get(timestamp) is None:
            community_data[id_landkreis][timestamp] = line
    
    accumulated_communities = _get_accumulated_data(community_data)
    return accumulated_communities


def _get_accumulated_data(rearranged_data: Dict[str, Dict[str, Dict]]) -> List[Dict[str, Any]]:
    '''
    For each community: sort by timestamp and add accumulated case numbers from prev. entry
    '''
    accumulated_communities: List[Dict[str, Any]] = []
    
    for timestamp_data in rearranged_data.values():  # per community or per state
        timestamps = list(timestamp_data.keys())
        timestamps.sort()
        
        # init first timestamp_data
        timestamp_data[timestamps[0]]["cases"]: int = int(timestamp_data[timestamps[0]]["AnzahlFall"])
        timestamp_data[timestamps[0]]["deaths"]:int = int(timestamp_data[timestamps[0]]["AnzahlTodesfall"])

        #accumulated.append(timestamp_data[timestamps[0]])

        for i in range(1, len(timestamps)):
            previous_dat: Dict[str, Any] = timestamp_data[timestamps[i-1]]
            current_dat: Dict[str, Any] = timestamp_data[timestamps[i]]
            
            current_dat["cases"]: int = previous_dat["cases"] + int(current_dat["AnzahlFall"])
            current_dat["deaths"]: int = previous_dat["deaths"] + int(current_dat["AnzahlTodesfall"])

            accumulated_communities.append(current_dat)

    return accumulated_communities


if __name__ == '__main__':
    community_data = _load_csv_data("26-03-2020")
    accumulated_communities = enrich_data(community_data)

    field_names: List[str] = accumulated_communities[0].keys()
    today = get_date()
    with open(f"data/{today}/numbers_rki_germany_communities_accumulated.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=field_names, delimiter=";")
        writer.writeheader()
        writer.writerows(accumulated_communities)

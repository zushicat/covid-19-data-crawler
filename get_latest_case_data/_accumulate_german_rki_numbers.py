'''
The RKI data per day reflects newly reported cases (per community), hence this accumulation script.
'''


import csv
import json
from typing import Any, Dict, List

from ._by_date import get_date


def enrich_data(data_in: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    '''
    Make dict: community -> timestamp -> acc. data for community for consec. timestamp
    '''
    community_data: Dict[str, List[Dict[str, Dict]]] = {}
    for line in data_in:
        id_landkreis: int = line["ags"]
        timestamp: int = int(line["reportDate_timestamp"])
        
        if community_data.get(id_landkreis) is None:
            community_data[id_landkreis] = {}
        if community_data[id_landkreis].get(timestamp) is None:
            community_data[id_landkreis][timestamp] = []
        community_data[id_landkreis][timestamp].append(line)
    
    community_data = _reduce_data_in_timestamp(community_data)
    accumulated_communities = _get_accumulated_data(community_data)
    return accumulated_communities


def _reduce_data_in_timestamp(community_data: Dict[str, List[Dict[str, Dict]]]) -> Dict[str, Dict[str, Dict]]:
    for ags, ags_data in community_data.items():
        for timestamp, timestamp_data in ags_data.items():
            tmp = None
            for data in timestamp_data:
                if tmp is None:
                    tmp = data
                    tmp["cases_day"] = 0
                    tmp["deaths_day"] = 0
                    tmp["recovered_day"] = 0
                tmp["cases_day"] += data["cases_day"]
                tmp["deaths_day"] += data["deaths_day"]
                tmp["recovered_day"] += data["recovered_day"]
            community_data[ags][timestamp] = tmp
    return community_data


def _get_accumulated_data(rearranged_data: Dict[str, Dict[str, Dict]]) -> List[Dict[str, Any]]:
    '''
    For each community: sort by timestamp and add accumulated case numbers from prev. entry
    '''
    accumulated_communities: List[Dict[str, Any]] = []
    
    for timestamp_data in rearranged_data.values():  # per community or per state
        timestamps = list(timestamp_data.keys())
        timestamps.sort()
        
        # init first timestamp_data
        timestamp_data[timestamps[0]]["cases"]: int = int(timestamp_data[timestamps[0]]["cases_day"])
        timestamp_data[timestamps[0]]["deaths"]:int = int(timestamp_data[timestamps[0]]["deaths_day"])
        timestamp_data[timestamps[0]]["recovered"]:int = int(timestamp_data[timestamps[0]]["recovered_day"])

        #accumulated.append(timestamp_data[timestamps[0]])

        for i in range(1, len(timestamps)):
            previous_dat: Dict[str, Any] = timestamp_data[timestamps[i-1]]
            current_dat: Dict[str, Any] = timestamp_data[timestamps[i]]
            
            current_dat["cases"]: int = previous_dat["cases"] + int(current_dat["cases_day"])
            current_dat["deaths"]: int = previous_dat["deaths"] + int(current_dat["deaths_day"])
            current_dat["recovered"]: int = previous_dat["recovered"] + int(current_dat["recovered_day"])
            
            accumulated_communities.append(current_dat)

    return accumulated_communities

'''
Request wikidata community data once and save in /data
'''

import csv
import json
from typing import Any, Dict, List

from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

sparql.setQuery("""
    SELECT DISTINCT ?nodeLabel ?ags ?population ?area
    WHERE
    {
        ?node wdt:P17 wd:Q183 .
        ?node wdt:P440 ?ags .
        ?node wdt:P1082 ?population .
        ?node wdt:P2046 ?area .
      
        SERVICE wikibase:label { bd:serviceParam wikibase:language "de" }
    }
    ORDER BY ?nodeLabel
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

community_data: List[Dict[str, Any]] = []
for r in results["results"]["bindings"]:
    # nodeLabel ags population area
    try:
        tmp = {
            "ags": r["ags"]["value"],
            "community_nam": r["nodeLabel"]["value"],
            "population_number": int(float(r["population"]["value"])),
            "population_density": int(float(r["population"]["value"])/float(r["area"]["value"]))
        }
        community_data.append(tmp)
    except Exception as e:
        print(e)
        continue

field_names: List[str] = community_data[0].keys()
with open(f"data/wikidata_community_data.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=field_names, delimiter=";")
    writer.writeheader()
    writer.writerows(community_data)

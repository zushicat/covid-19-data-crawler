'''
Request wikidata country data once (german country name label) and save in /data
'''

import csv
import json
from typing import Any, Dict, List

from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

sparql.setQuery("""
    SELECT DISTINCT ?countryLabel ?country ?isoCodeLabel ?population ?area
    WHERE
    {
        ?country wdt:P31 wd:Q3624078 .
        ?country wdt:P1082 ?population .
        ?country wdt:P297 ?isoCode .
        ?country wdt:P2046 ?area .
        
        # not a former country
        # and no an ancient civilisation (needed to exclude ancient Egypt)
        FILTER NOT EXISTS {?country wdt:P31 wd:Q3024240}
        FILTER NOT EXISTS {?country wdt:P31 wd:Q28171280}
        
        SERVICE wikibase:label { bd:serviceParam wikibase:language "de" }
    }
    ORDER BY ?countryLabel
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

country_data: List[Dict[str, Any]] = []
for r in results["results"]["bindings"]:
    try:
        tmp = {
            "countryCode": r["isoCodeLabel"]["value"],
            "country_name_german": r["countryLabel"]["value"],
            "population_number": int(float(r["population"]["value"])),
            "population_density": int(float(r["population"]["value"])/float(r["area"]["value"]))
        }
        country_data.append(tmp)
    except Exception as e:
        print(r["countryLabel"]["value"], e)
        continue

field_names: List[str] = country_data[0].keys()
with open(f"data/wikidata_nations_data.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=field_names, delimiter=";")
    writer.writeheader()
    writer.writerows(country_data)

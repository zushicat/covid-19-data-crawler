'''
Scrape the latest data from the official website of Cologne, Germany
Url: https://www.stadt-koeln.de/leben-in-koeln/gesundheit/infektionsschutz/corona-virus/corona-virus-anzahl-der-bestaetigten-faelle-koeln
'''

import csv
from datetime import datetime
import locale
import os
from typing import Any, List, Dict

from ._by_date import get_date

from bs4 import BeautifulSoup
import requests


DIRNAME = os.path.dirname(__file__)

def scrape_stadt_koeln_data():
    url = "https://www.stadt-koeln.de/leben-in-koeln/gesundheit/infektionsschutz/corona-virus/corona-virus-anzahl-der-bestaetigten-faelle-koeln"
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    table_container = soup.find(id="ziel_text_0_21").find("table")

    formatted_col_names = {
        "Datum": "reportDate",
        "bestätigte Kölner Fälle": "cases",
        "Infizierte Kölner in häuslicher Quarantäne": "quaratined",
        "Patienten in stationärer Behandlung": "hospitalized",
        "Kölner als geheilt entlassen": "recovered",
        "Aktuell Infizierte in Köln": "infected",
        "Kölner Todesfälle": "deaths"
    }

    column_names: List[str] = []
    cologne_data: List[Dict[str, Any]] = []
    
    first_row = True
    for row in table_container.find("tbody").contents:
        if first_row is True:
            for i, col in enumerate(row):
                col_name: str = formatted_col_names[col.text]
                column_names.append(col_name)
            first_row = False
            continue
        tmp = {}
        for i, col in enumerate(row):
            if column_names[i] == "reportDate":
                formatted_date = col.text
                formatted_date = formatted_date.replace(".", "")  # try to catch typos in date
                formatted_date = datetime.strptime(formatted_date, "%d%m").strftime("%d-%m-2020")  # 1. März -> 01-03-2020
                tmp[column_names[i]]:str = formatted_date
            else:
                try:
                    tmp[column_names[i]]:int = int(col.text.strip().replace(".", ""))
                except Exception:
                    tmp[column_names[i]]:int = -1  # no entry
        
        # if quaratined column is missing (since 14.05.2020)
        if tmp.get("quaratined") is None:
            tmp["quaratined"] = tmp["infected"] - tmp["hospitalized"]

        # add static population data (city, not metro)
        tmp["population_number"] = 1085664  
        tmp["population_density"] = 2700
        tmp["ags"] = "5315"
        tmp["source"] = "Stadt Köln"

        cologne_data.append(tmp)
    
    today = get_date()
    field_names: List[str] = cologne_data[0].keys()
    with open(f"data/{today}/city_cologne_germany.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=field_names, delimiter=",")
        writer.writeheader()
        writer.writerows(cologne_data)


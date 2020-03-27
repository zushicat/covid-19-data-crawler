'''
Scrape the latest data from the official website of Cologne, Germany
Url: https://www.stadt-koeln.de/leben-in-koeln/gesundheit/infektionsschutz/corona-virus/corona-virus-anzahl-der-bestaetigten-faelle-koeln

(The data table for the line chart is hidden.)
'''

import csv
from datetime import datetime
import locale
import os
from typing import Any, List, Dict

from ._by_date import get_date

from bs4 import BeautifulSoup
import requests


locale.setlocale(locale.LC_ALL, '')  # thx to not following date format standards in source: use german local settings

DIRNAME = os.path.dirname(__file__)

def scrape_stadt_koeln_data():
    url = "https://www.stadt-koeln.de/leben-in-koeln/gesundheit/infektionsschutz/corona-virus/corona-virus-anzahl-der-bestaetigten-faelle-koeln"
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    table_container = soup.find(id="datatable_0_2")

    formatted_col_names = {
        "": "reportDate",
        "bestätigte Fälle": "cases",
        "häusliche Quarantäne": "quaratined",
        "stationäre Behandlung": "hospitalized",
        "Als geheilt entlassen": "recovered"
    }

    column_names: List[str] = []
    for x in table_container.find("thead").find("tr").contents:
        col_name: str = formatted_col_names[x.text]
        column_names.append(col_name)

    cologne_data: List[Dict[str, Any]] = []
    for row in table_container.find("tbody").contents:
        tmp = {}
        for i, col in enumerate(row):
            if column_names[i] == "reportDate":
                formatted_date = f"{col.text}"
                formatted_date = datetime.strptime(formatted_date, "%d. %B").strftime("%d-%m-2020")  # 1. März -> 01-03-2020
                tmp[column_names[i]]:str = formatted_date
            else:
                tmp[column_names[i]]:int = int(col.text)
        
        # add static population data (city, not metro)
        tmp["population_number"] = 1085664  
        tmp["population_density"] = 2700
        tmp["ags"] = "5315"

        cologne_data.append(tmp)
    

    today = get_date()
    field_names: List[str] = cologne_data[0].keys()
    with open(f"data/{today}/city_cologne_germany.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=field_names, delimiter=";")
        writer.writeheader()
        writer.writerows(cologne_data)


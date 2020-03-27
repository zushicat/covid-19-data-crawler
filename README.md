# covid-19-data-crawler
Get latest data updates of covid-19 numbers from different sources (with focus on Germany as of now).

There is quite a gap between the overall numbers from Robert Koch Institute and (well respected) news outlets, hence this data crawler of different sources (as of now with focus on Germany).   



## Crawled Sources

### 1 - Robert Koch Institute (RKI)
https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0/geoservice  

Requested attributes:
- AnzahlFall
- AnzahlTodesfall
- Meldedatum (is timestamp)
- IdLandkreis
- IdBundesland
- Landkreis

### 2 - Stadt Köln (Northrhine-Westphalia, Germany)
This is out of very personal interest in the numbers within my immediate vicinity. Yikes.

Scrape datatable of the overview page:   
https://www.stadt-koeln.de/leben-in-koeln/gesundheit/infektionsschutz/corona-virus/corona-virus-anzahl-der-bestaetigten-faelle-koeln

### 3 - News outlets
Zeit Online (ZON), Berliner Morgenpost

#### a - The API by jgehrcke
Numbers on state level (which I additionally accumulated to national level)  
For details, see: https://github.com/jgehrcke/covid-19-germany-gae

#### b - ZON
ZON now additionally provides international and community level data (see comments with JSON links in /get_latest_case_data/_get_ZON_data.py) which I both request.



## Usage
If you like to request the data yourself, just call request_data.py. Csv files are then saved in a directory named by date of request (under /data).  
**All data is enriched with additional information about the location (ISO state/country codes and information about population numbers/density).**

Otherwise just get the csv files in directory of latest date.

- 1 - RKI
  - communities_germany_rki
- 2 - Stadt Köln
  - city_cologne_germany.csv
- 3a 
  - national_germany_news_api.csv
  - states_germany_news_api.csv
- 3b - News Outlets
  - nations_ZON.csv
  - communities_ZON.csv

The data points of all csv files are saved as  "tidy" (or "long") data instead of "wide" data, meaning:  
Each date for each location is represented by a line instead of one line per location with all the dates as columns.

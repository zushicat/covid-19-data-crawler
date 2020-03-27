## Get lates data

### Scrape daily data from Stadt Köln
Script: scrape_stadt_koeln.py

Source: https://www.stadt-koeln.de/leben-in-koeln/gesundheit/infektionsschutz/corona-virus/corona-virus-anzahl-der-bestaetigten-faelle-koeln

Saves data in:
- city_cologne_germany.csv


### Colaborative data from coronascraper
International afford by crowd sourcing / volunteers to collect latest numbers  
(Different formats available.)

Source: https://coronadatascraper.com/#timeseries.csv

Manually downloaded and saved in:
- coronal_scaper_timeseries.csv


### Request data from Robert-Koch Institute
Script: request_german_rki_api.py

Uses the RKI API found here:  
https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0/geoservice  
requesting:
- AnzahlFall
- AnzahlTodesfall
- Meldedatum (is timestamp)
- IdLandkreis
- IdBundesland
- Landkreis

The timestamp of reported cases is additionally formatted in human readable date. Also, the ISO state code is additionally provided.

The numbers are newly reported cases and not accumulated.

Saves data in:
- data/numbers_rki_germany_community.csv


### Accumulate case numbers of Robert-Koch Institute data
Script: accumulate_german_rki_numbers

Accumulate the daily new reported cases (and deaths) per community.


### Request data from German news outlets
Script: request_german_news_outlets.py

There is a certain gap between the official (and better validated, hence more reliable) numbers of the Robert-Koch Institute and the aggregation of selected, highly regarded news outlets (in this case Zeit Online and Morgenpost). This gap happens due to reporting and verification delays between health agencies of different levels and the RKI. (No conspiracy found anywhere, this is a quality measure.)  
The data coming from both sources are aggregations of the numbers provided by public health agencies on local and state level.  
For highly dependable numbers in the long run, one might better rely on the official numbers by the Robert-Koch Institute. Still these numbers, updated in higher frequencies, are most usefull for short term usage.  

This scripts requests the latest numbers on state level and accumulates all numbers to national level.  
Saves data in:
- data/numbers_news_outlets_germany_national.csv
- data/numbers_news_outlets_germany_states.csv  

These numbers are accumulated.

For API details, see:  
https://github.com/jgehrcke/covid-19-germany-gae


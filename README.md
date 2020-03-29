# covid-19-data-crawler
Get latest data updates of covid-19 numbers from different sources (with main focus on Germany as of now).

There is quite a gap between the overall numbers from Robert Koch Institute and (well respected) news outlets, hence this data crawler of different sources.   

For details about this discrepancy you might want to take a look i.e. at this discussion (Johns Hopkins CSSE (JHU) repository):  
https://github.com/CSSEGISandData/COVID-19/issues/1008



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

**Update:** I normalized the german attribute naming.

### 2 - Stadt Köln (North Rhine-Westphalia, Germany)
This is out of very personal interest in the numbers within my immediate vicinity. Yikes.

Scrape datatable of the overview page:   
https://www.stadt-koeln.de/leben-in-koeln/gesundheit/infektionsschutz/corona-virus/corona-virus-anzahl-der-bestaetigten-faelle-koeln

There are daily updates by press releases but the tech team responsible for the chart (and datatable) obviously don't update on the weekend. **Boo!**

### 3 - News outlets
Data taken from Zeit Online (ZON) and Berliner Morgenpost

#### a - API by jgehrcke
Numbers on state level (which I additionally accumulated to national level)  
For details, see: https://github.com/jgehrcke/covid-19-germany-gae

#### b - ZON
ZON now additionally provides international and community level data (see comments with JSON links in /get_latest_case_data/_get_ZON_data.py) which I both request.



## Usage
Download (or clone) and run project (from pipenv environment):  
- open terminal
- install pipenv (see: https://pypi.org/project/pipenv/)
```
$ pip install pipenv    (OR in case of your sytem bitching about pip version or permissions:)
$ sudo pip3 install pipenv 
```
- change to the downloaded/cloned project directory
```
$ cd soemthing/something/covid-19-data-crawler
```
- start pipenv shell (you can exit the shell with "exit")
```
$ pipenv shell
```

If you don't want to use pipenv, see Pipfile for installed packages.


### Call request script
Call script and request all data sources:
```
$ python request_data.py
```

Addintionally you can use following flags (with --all as default):
```
Options:
  --all      Request all sources
  --rki      Request Robert Koch Institute
  --news     Request news outlet API by jgehrcke
  --zon-i    Request ZON international numbers
  --zon-c    Request ZON community numbers
  --cologne  Request data for city of Cologne, Germany
  --help     Show this message and exit.
```

i.e.
```
$ python request_data.py --cologne
```



### Requested data directory
Data of requested sources is stored in csv format (delimiter=",") in a directory named by date of request under /data. 

**All data is enriched with additional information about the location (ISO state/country codes and information about population numbers/density).**

Otherwise just get the csv files in directory of latest date.

- 1 - RKI
  - communities_germany_rki
- 2 - Stadt Köln
  - city_cologne_germany.csv
- 3a - News Outlets (Zeit Online, Berliner Morgenblatt)
  - national_germany_news_api.csv
  - states_germany_news_api.csv
- 3b - Zeit Online
  - nations_ZON.csv
  - communities_ZON.csv

The data points of all csv files are saved as "tidy" (or "long") data instead of "wide" data, meaning:  
Each date for each location is presented in a row instead of one row per location with all the dates as columns.

Please keep in mind that latest data (in dated directory) not necessarily includes the latest numbers of this date, since this depends on the update cycles of respective sources.


## More Sources

### Germany
Big shoutout to **https://github.com/jgehrcke**  
https://github.com/jgehrcke/covid-19-germany-gae   
who's not only providing one of the used APIs (see: 3a) but also has tons of additional sources listed.  


**Risklayer** (an independent think tank based in Karlsruhe, Germany) is providing a comprehensive spreadsheet:   
https://docs.google.com/spreadsheets/d/1wg-s4_Lz2Stil6spQEYFdZaBEp8nWW26gVyfHqvcl8s/edit?pli=1#gid=0  

Company page and press releases: 
- http://www.risklayer.com/de/
- http://www.risklayer.com/post_list

Data explorer:
- http://risklayer-explorer.com/event/6/detail  
- Used by Tagesspiegel: https://interaktiv.tagesspiegel.de/lab/karte-sars-cov-2-in-deutschland-landkreise/  


Another Datavisualization using Risklayer data by Conterra, Germany:
https://corona.conterra.de/?lang=de


**Deutsche Interdisziplinäre Vereinigung für Intensiv- und Notfallmedizin e.V. - DIVI**  
https://divi.de/  

A register of ICU beds in german hospitals and their current occupancy / workload:   
- https://divi.de/register/intensivregister
- https://divi.de/register/kartenansicht  (resp.: https://diviexchange.z6.web.core.windows.net/)

(As of now I could not find any timeseries for this source.)


### International
A data community driven project with COVID-19 Coronavirus data scraped from government and curated data sources:   
https://coronadatascraper.com
with several formats of timesseries (csv and JSON).   


***Johns Hopkins CSSE (JHU)***:   
https://github.com/CSSEGISandData/COVID-19/

The timeseries (as wide data) can be found under:   
https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series  


**NYTimes** Covid-19 Data by US states and counties:  
https://github.com/nytimes/covid-19-data

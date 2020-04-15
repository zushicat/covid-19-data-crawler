# covid-19-data-crawler
Get latest data updates of covid-19 numbers from different sources (with main focus on Germany as of now).

There is quite a gap between the overall numbers from Robert Koch Institute and (well respected) news outlets, hence this data crawler of different sources.   

For details about this discrepancy you might want to take a look i.e. at this discussion (Johns Hopkins CSSE (JHU) repository):  
https://github.com/CSSEGISandData/COVID-19/issues/1008    


In case you're interested in infection spread models based on this data, have a look here:   
https://github.com/zushicat/infection-modeling (right now Cologne, Germany, only)



## Crawled Sources

### 1 - Robert Koch Institute (RKI)
https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0/geoservice  

Requested attributes:
- AnzahlFall
- AnzahlTodesfall
- AnzahlGenesen
- Meldedatum (is timestamp)
- IdLandkreis
- IdBundesland
- Landkreis

**Update:** I normalized the german attribute naming.    
**Update:** Added number of recovered individuals (per day and accumulated).     
Please note: There is a strange behavior regarding the numbers of recoveries in the beginning of some community timeseries, where these numbers per day are the same as for cases per day. (Over time, this behavior changes which is reflected in the accumulated numbers.)    
See this example request: https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/query?where=IdLandkreis=8111&outFields=Meldedatum,AnzahlFall,AnzahlGenesen,AnzahlTodesfall,Landkreis&outSR=4326    
¯\\_(ツ)_/¯    
I just take this as a given fact (for whatever underlying reason) but wanted to highlight this. Looking closer to the recovery numbers for some communities, I would take this data with a grain of salt, anyway.    
**Update** There are markers for deaths and recovered cases (NeuTodesfall, NeuGenesen) but those don't help at all because cases are just marked as deceased or recovered without being bound to a date. Hence it's impossible to put those numbers in a timeseries.     
(You might want to have a look at this discussion: https://www.arcgis.com/home/item.html?id=dd4580c810204019a7b8eb3e0b329dd6)    
**Maybe best practice is to just ignore the RKI numbers for deaths and recoveries (at least for now).**    


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


### 4 - Tagesspiegel (Risklayer)
**Update** Added request of Tagesspiegel google spreadsheets which is basically (I think collected) data from Risklayer (for more information about Risklayer, see below in 'More Sources').   

I used the spreadsheets of accumulated numbers for
- cases (earliest date: 04.03.2020)
- deaths (earliest date: 30.03.2020)
- recovery (earliest date: 27.03.2020)
   
Please refer to the top comment in    
/get_latest_case_data/_get_tagesspiegel_data.py    
for the used data links.   

The data is not as complete as one would wish, especially for recoveries and deaths there is sometimes data missing or apparently not daily updated (depending on the community, I guess).   
These gaps are stores as null (not 0), hence the missing difference to the respective first occuring numbers per community. Please take that in consideration when processing this data.


### 5 - Berliner Morgenpost
**Update** Added new source    
Berliner Morgenpost is doing a great job of collecting data on different levels:    
- 0: nation level (international)
- 1: state level (different countries)
- 2: district level (Germany)

As far as I can see right now, this is the most comprehensive data source incl. recovered and deceased cases.    

Data url:    
https://funkeinteraktiv.b-cdn.net/history.v4.csv    

The respective original sources can also be found in the csv file (which I drop here for practicality).    

Interactive usage of this data:    
https://interaktiv.morgenpost.de/corona-virus-karte-infektionen-deutschland-weltweit/    


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
$ cd something/something/covid-19-data-crawler
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
  --ts       Request Tagesspiegel community numbers
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
- 4 - Tagesspiegel (Risklayer)
  - communities_tagesspiegel.csv
- 5 - Berliner Morgenpost
  - communities_germany_mopo_b.csv
  - nations_mopo_b.csv
  - states_AU_mopo_b.csv
  - states_CA_mopo_b.csv
  - states_CN_mopo_b.csv
  - states_DE_mopo_b.csv

**Update**    
I additionally merged RKI and Tagesspiegel (Risklayer) data:
- communities_germany_merged_rki_ts.csv    
~~(This merge makes the oddness of the RKI recovered numbers in the timeseries even more apparent.)~~    
Regarding the numbers for reccovered and deceased cases, please see notes under (1).    


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
with several formats of timeseries (csv and JSON).   


***Johns Hopkins CSSE (JHU)***:   
https://github.com/CSSEGISandData/COVID-19/

The timeseries (as wide data) can be found under:   
https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series  


**NYTimes** Covid-19 Data by US states and counties:  
https://github.com/nytimes/covid-19-data

import os

from get_latest_case_data._request_german_news_outlets import request_news_outlet_api
from get_latest_case_data._request_german_rki_api import request_rki_api
from get_latest_case_data._scrape_stadt_koeln import scrape_stadt_koeln_data
from get_latest_case_data._get_ZON_data import get_ZON_communities_data, get_ZON_international_data
from get_latest_case_data._get_tagesspiegel_data import get_TS_communities_data

from process_data._merge_accumulate_rki_ts import merge_accumulate_rki_ts

import click


@click.command()
@click.option('--all', 'requested_source', default=True, flag_value='all', help='Request all sources')
@click.option('--rki', 'requested_source', default=False, flag_value='rki', help='Request Robert Koch Institute')
@click.option('--news', 'requested_source', default=False, flag_value='news', help='Request news outlet API by jgehrcke')
@click.option('--zon-i', 'requested_source', default=False, flag_value='zon_i', help='Request ZON international numbers')
@click.option('--zon-c', 'requested_source', default=False, flag_value='zon_c', help='Request ZON community numbers')
@click.option('--ts', 'requested_source', default=False, flag_value='ts', help='Request Tagesspiegel community numbers')
@click.option('--cologne', 'requested_source', default=False, flag_value='cologne', help='Request data for city of Cologne, Germany')
def request_sources(requested_source):
    '''
    Request sources by options
    '''
    functions = {
        "news": request_news_outlet_api,
        "rki": request_rki_api,
        "cologne": scrape_stadt_koeln_data,
        "zon_i": get_ZON_international_data,
        "zon_c": get_ZON_communities_data,
        "ts": get_TS_communities_data
    }

    if requested_source == "all":
        for fkt in functions.values():
            fkt()
    else:
        functions[requested_source]()
    
    # ***
    # process some files (merge / accumulate)
    try:
        merge_accumulate_rki_ts(os.listdir("data"))
    except:
        pass

if __name__ == '__main__':
    request_sources()

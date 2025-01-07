"""
    Scraper for the project. Uses Sreality.cz.
"""

import requests # for making HTTP requests
import pandas as pd
import time
import random


def get_sreality(category_type, page, category_main = 1, locality_region = 10):
    base_url = ("https://www.sreality.cz/api/cs/v2/estates?category_main_cb=" + str(category_main) + "&category_type_cb="
                + str(category_type) + "&locality_region_id=" + str(locality_region) + "&per_page=33&page=" + str(page))
    r_sleep = random.uniform(1.01, 1.81)
    time.sleep(r_sleep)

    try:
        # Use headers as Sreality.cz obfuscates prices
        r = requests.get(base_url, headers = {"User-Agent": "Mozilla/5.0"})
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    return r.json()


def convert_sreality_to_df(data):
    return pd.DataFrame(data['_embedded']['estates'])


def get_all_sreality(category_type: int=1):
    page = 1
    list_of_dfs = []

    while True:
        json_data = get_sreality(category_type, page)
        if len(json_data['_embedded']['estates']) == 0:
            break
        df = convert_sreality_to_df(json_data)
        list_of_dfs.append(df)
        page += 1
    return pd.concat(list_of_dfs)


def run():
    get_all_sreality()

# TODO: parsing, cleaning, matching
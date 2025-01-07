"""
    Scraper for the project. Uses Sreality.cz for gathering the data.
"""

import requests # for making HTTP requests
import pandas as pd
import time
import random


# Use headers as Sreality.cz obfuscates prices
headers_user = {"User-Agent": "Mozilla/5.0"}


def get_sreality(category_type, page, category_main = 1, locality_region = 10):
    base_url = ("https://www.sreality.cz/api/cs/v2/estates?category_main_cb=" + str(category_main) + "&category_type_cb="
                + str(category_type) + "&locality_region_id=" + str(locality_region) + "&per_page=33&page=" + str(page))
    r_sleep = random.uniform(1.01, 1.81)
    time.sleep(r_sleep)

    try:
        r = requests.get(base_url, headers = headers_user)
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    return r.json()


def get_description(code):
    base_url = "https://www.sreality.cz/api/cs/v2/estates/" + str(code)
    r_sleep = random.uniform(0.5, 0.7)
    time.sleep(r_sleep)

    try:
        r = requests.get(base_url, headers=headers_user)
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    return r.json()


def convert_sreality_to_df(data):
    return pd.DataFrame(data['_embedded']['estates'])


def convert_description_to_df(json_data):
    db = pd.DataFrame()

    # region Parsing to established format
    db["code"] = [str(json_data["recommendations_data"]["hash_id"])]
    db["description"] = str(json_data["text"]["value"])
    db["meta_description"] = str(json_data["meta_description"])
    db["category_main_cb"] = int(json_data["seo"]["category_main_cb"])
    db["category_sub_cb"] = int(json_data["seo"]["category_sub_cb"])
    db["category_type_cb"] = int(json_data["seo"]["category_type_cb"])
    db["broker_id"] = str(json_data["_embedded"]["seller"]["user_id"])
    db["broker_company"] = str(json_data["_embedded"]["seller"]["_embedded"]["premise"]["name"])
    db["furnished"] = int(json_data["recommendations_data"]["furnished"])
    db["locality_gps_lat"] = float(json_data["recommendations_data"]["locality_gps_lat"])
    db["locality_gps_lon"] = float(json_data["recommendations_data"]["locality_gps_lon"])
    db["object_type"] = int(json_data["recommendations_data"]["object_type"])
    db["parking_lots"] = int(json_data["recommendations_data"]["parking_lots"])
    db["locality_street_id"] = int(json_data["recommendations_data"]["locality_street_id"])
    db["locality_district_id"] = int(json_data["recommendations_data"]["locality_district_id"])
    db["locality_ward_id"] = int(json_data["recommendations_data"]["locality_ward_id"])
    db["locality_region_id"] = int(json_data["recommendations_data"]["locality_region_id"])
    db["locality_quarter_id"] = int(json_data["recommendations_data"]["locality_quarter_id"])
    db["locality_municipality_id"] = int(json_data["recommendations_data"]["locality_municipality_id"])
    db["locality_country_id"] = int(json_data["recommendations_data"]["locality_country_id"])
    db["terrace"] = int(json_data["recommendations_data"]["terrace"])
    db["balcony"] = int(json_data["recommendations_data"]["balcony"])
    db["loggia"] = int(json_data["recommendations_data"]["loggia"])
    db["basin"] = int(json_data["recommendations_data"]["basin"])
    db["cellar"] = int(json_data["recommendations_data"]["cellar"])
    db["building_type"] = int(json_data["recommendations_data"]["building_type"])
    db["object_kind"] = int(json_data["recommendations_data"]["object_kind"])
    db["ownership"] = int(json_data["recommendations_data"]["ownership"])
    db["low_energy"] = int(json_data["recommendations_data"]["low_energy"])
    db["easy_access"] = int(json_data["recommendations_data"]["easy_access"])
    db["building_condition"] = int(json_data["recommendations_data"]["building_condition"])
    db["garage"] = int(json_data["recommendations_data"]["garage"])
    db["room_count_cb"] = int(json_data["recommendations_data"]["room_count_cb"])
    db["energy_efficiency_rating_cb"] = int(json_data["recommendations_data"]["energy_efficiency_rating_cb"])
    for item in json_data["items"]:
        if item["name"] == "Poznámka k ceně":
            db["note_about_price"] = item["value"]
        elif item["name"] == "ID zakázky":
            db["id_of_order"] = item["value"]
        elif item["name"] == "Aktualizace":
            db["last_update"] = item["value"]
        elif item["name"] == "Stavba":
            db["material"] = item["value"]
        elif item["name"] == "Stav objektu":
            db["age_of_building"] = item["value"]
        elif item["name"] == "Vlastnictví":
            db["ownership_type"] = item["value"]
        elif item["name"] == "Podlaží":
            db["floor"] = item["value"]
        elif item["name"] == "Užitná plocha":
            db["usable_area"] = item["value"]
        elif item["name"] == "Plocha podlahová":
            db["floor_area"] = item["value"]
        elif item["name"] == "energy_efficiency_rating":
            db["energy_efficiency_rating"] = item["value"]
        elif item["name"] == "Bezbariérový":
            db["no_barriers"] = item["value"]
        elif item["name"] == "Datum zahájení prodeje":
            db["start_of_offer"] = item["value"]
    # endregion

    return db


def get_all_sreality(category_type: int=1):
    page = 1
    list_of_dfs = []

    while True:
        json_data = get_sreality(category_type, page)
        if len(json_data['_embedded']['estates']) == 0:
            break
        list_of_dfs.append(convert_sreality_to_df(json_data))
        page += 1

    # Create DataFrame and include only code (hash) and price
    db = pd.concat(list_of_dfs)
    db = db[["hash_id", "price"]]

    # Remove adverts costing 1 CZK
    db = db.drop(db[db.price == 1].index).reset_index(drop=True)

    return db


def get_all_description(db):
    list_of_dfs = []

    for code in list(db["hash_id"]):
        json_data = get_description(code)
        if len(json_data) == 1:
            pass # Invalid code TODO: Throw error?
        list_of_dfs.append(convert_description_to_df(json_data))

    return pd.concat(list_of_dfs)


def parse(base, desc):
    pass



def run():
    df_base = get_all_sreality()
    df_desc = get_all_description(df_base)
    parse(df_base, df_desc)





# TODO: matching
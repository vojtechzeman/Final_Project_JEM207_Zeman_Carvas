"""
    Scraper for the project. Uses Sreality.cz for gathering the data.
    Run by calling run_online() (see run_online() description)
    Operates with buy.json and rent.json
"""

import requests # for making HTTP requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
import random

# Declare option to buy or to rent
intention = {
    "buy": 1,
    "rent": 2
}

# Get current date
date =  datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

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


def convert_sreality_to_df(json_data):
    return pd.DataFrame(json_data['_embedded']['estates'])


def convert_description_to_df(json_data):
    db = pd.DataFrame()

    elementRenameTable = {
    "code": lambda: int(json_data["recommendations_data"]["hash_id"]),
    "description": lambda: str(json_data["text"]["value"]),
    "meta_description": lambda: str(json_data["meta_description"]),
    "category_main_cb": lambda: int(json_data["seo"]["category_main_cb"]),
    "category_sub_cb": lambda: int(json_data["seo"]["category_sub_cb"]),
    "category_type_cb": lambda: int(json_data["seo"]["category_type_cb"]),
    "broker_id": lambda: str(json_data["_embedded"]["seller"]["user_id"]),
    "broker_company": lambda: str(json_data["_embedded"]["seller"]["_embedded"]["premise"]["name"]),
    "furnished": lambda: int(json_data["recommendations_data"]["furnished"]),
    "locality_gps_lat": lambda: float(json_data["recommendations_data"]["locality_gps_lat"]),
    "locality_gps_lon": lambda: float(json_data["recommendations_data"]["locality_gps_lon"]),
    "object_type": lambda: int(json_data["recommendations_data"]["object_type"]),
    "parking_lots": lambda: int(json_data["recommendations_data"]["parking_lots"]),
    "locality_street_id": lambda: int(json_data["recommendations_data"]["locality_street_id"]),
    "locality_district_id": lambda: int(json_data["recommendations_data"]["locality_district_id"]),
    "locality_ward_id": lambda: int(json_data["recommendations_data"]["locality_ward_id"]),
    "locality_region_id": lambda: int(json_data["recommendations_data"]["locality_region_id"]),
    "locality_quarter_id": lambda: int(json_data["recommendations_data"]["locality_quarter_id"]),
    "locality_municipality_id": lambda: int(json_data["recommendations_data"]["locality_municipality_id"]),
    "locality_country_id": lambda: int(json_data["recommendations_data"]["locality_country_id"]),
    "terrace": lambda: int(json_data["recommendations_data"]["terrace"]),
    "balcony": lambda: int(json_data["recommendations_data"]["balcony"]),
    "loggia": lambda: int(json_data["recommendations_data"]["loggia"]),
    "basin": lambda: int(json_data["recommendations_data"]["basin"]),
    "cellar": lambda: int(json_data["recommendations_data"]["cellar"]),
    "building_type": lambda: int(json_data["recommendations_data"]["building_type"]),
    "object_kind": lambda: int(json_data["recommendations_data"]["object_kind"]),
    "ownership": lambda: int(json_data["recommendations_data"]["ownership"]),
    "low_energy": lambda: int(json_data["recommendations_data"]["low_energy"]),
    "easy_access": lambda: int(json_data["recommendations_data"]["easy_access"]),
    "building_condition": lambda: int(json_data["recommendations_data"]["building_condition"]),
    "garage": lambda: int(json_data["recommendations_data"]["garage"]),
    "room_count_cb": lambda: int(json_data["recommendations_data"]["room_count_cb"]),
    "energy_efficiency_rating_cb": lambda: int(json_data["recommendations_data"]["energy_efficiency_rating_cb"]),
    }
    for element, func in elementRenameTable.items():
        try:
            db[element] = [func()]
        except KeyError:
            db[element] = [np.nan]

    itemRenameTable = {
        "Poznámka k ceně": "note_about_price",
        "ID zakázky": "id_of_order",
        "Aktualizace": "last_update",
        "Stavba": "material",
        "Stav objektu": "age_of_building",
        "Vlastnictví": "ownership_type",
        "Podlaží": "floor",
        "Užitná ploch": "usable_area",
        "Plocha podlahová": "floor_area",
        "Celková plocha": "total_area",
        "Výtah": "elevator",
        "Energetická náročnost budovy": "energy_efficiency_rating",
        "Bezbariérový": "no_barriers",
        "Datum zahájení prodeje": "start_of_offer"
    }

    for item in json_data["items"]:
        if item["name"] in itemRenameTable:
            db[itemRenameTable[item["name"]]] = item["value"]
            del itemRenameTable[item["name"]]

    # Make sure all columns are filled either with data or NaN
    for item_left in itemRenameTable:
        db[itemRenameTable[item_left]] = np.nan
    # endregion

    return db


def get_all_sreality(category_type: int, times = 3):

    list_of_dbs = []

    for i in range(times):
        list_of_dfs = []
        page = 1
        while True:
            json_data = get_sreality(category_type, page)
            if len(json_data['_embedded']['estates']) == 0:
                break
            list_of_dfs.append(convert_sreality_to_df(json_data))
            page += 1
        list_of_dbs.append(pd.concat(list_of_dfs))


    db = pd.concat(list_of_dbs)

    db.drop_duplicates(subset=["hash_id"], inplace=True)

    # Remove adverts costing 1 CZK
    db.drop(db[db.price == 1].index, inplace=True)

    # Change id to code as it will be used for matching
    db.rename(columns={'hash_id':'code'}, inplace=True)

    # Get first image from nested dict in _links
    image = pd.json_normalize(pd.json_normalize(pd.json_normalize(db["_links"])["images"])[0]).rename(columns={"href": "image"})

    # Get locality from dict seo for creating links later
    locality = pd.json_normalize(db["seo"])["locality"]

    # Extract code and price
    db = db[["code", "price"]]

    db = db.reset_index(drop=True)
    return pd.concat([db, image, locality], axis = 1)


def get_all_description(db):
    list_of_dfs = []
    iter = 1

    for code in list(db["code"]):
        json_data = get_description(code)
        if len(json_data) == 1:
            continue  # Invalid code
        print("Getting details (" + str(iter) + ")")
        list_of_dfs.append(convert_description_to_df(json_data))
        iter += 1

    return pd.concat(list_of_dfs)


def clean(db):

    # Energy rating cleaning
    enrg = db["energy_efficiency_rating"]
    if type(enrg) == str and "Třída" in enrg:
        db["energy_efficiency_rating"] = enrg[6]

        if " č." in enrg:
            db["energy_efficiency_description"] = enrg[10:enrg.find(" č.")]
        else:
            db["energy_efficiency_description"] = enrg[10:]
    else:
        db["energy_efficiency_description"] = db["energy_efficiency_rating"] = np.nan

    # Add link column
    meta_desc = str(db["meta_description"])
    cat = meta_desc.split()[0].lower()
    if meta_desc.split()[1] == "atypické":
        intent = meta_desc.split()[6]
        size = "atypicky"
    else:
        intent = meta_desc.split()[5]
        size = meta_desc.split()[1]

    correction_table = {
        "prodeji": "prodej",
        "pronájmu": "pronajem"
        }

    intent = correction_table[intent]

    db["link"] = ("https://www.sreality.cz/detail/" + intent + "/" + cat + "/" + size + "/" + db["locality"] + "/" +
                  str(db["code"]))

    # Add columns for matching deleted adverts
    db["deleted"] = 0
    db["time of deletion"] = np.nan

    # Add timestamp
    db["timestamp"] = date
    return db


def parse(base, desc):
    db = pd.merge(base, desc, on='code')
    db = db.apply(clean, axis=1)
    return db


def run_online(intent):
    """
        Executes various functions to update buy.json or rent.json from Sreality.cz.
        :param intent: either "buy" or "rent"


        Works in this order: finds new listings and their details, finds and marks deleted listings,
        merges and saves to either buy.json or rent.json.
    """
    if intent not in ["buy", "rent"]:
        raise ValueError(f"""arg has to be either "buy" or "rent", not: {intent}""")

    cb_type = intention[intent]
    master_db = None

    # Check if buy.json or rent.json exist
    try:
        master_db = pd.read_json(f"last_scraping_for_modeling/{intent}.json")
        print(f"Found {intent}.json")
    except FileNotFoundError:
        print(f"No such file {intent}.json. No matching possible. Creating {intent}.json")
    print("Finding all listings from Sreality.cz")
    df_base = get_all_sreality(cb_type)

    if master_db is None:
        print("Found "+ str(df_base.shape[0]) + " listings")
        df_desc = get_all_description(df_base)
        print("Found details of " + str(df_desc.shape[0]) + " listings")
        master_db = parse(df_base, df_desc)
    else:
        # Only find details for where they are missing
        new_ids = df_base[~df_base["code"].isin(master_db["code"])]
        print("Found " + str(new_ids.shape[0]) + " new listings")
        print("Getting their details")
        if len(new_ids) != 0:
            new_ids_desc = get_all_description(new_ids)
            new_ids_complete = parse(new_ids, new_ids_desc)

        # Check for deleted listings and save them to deleted_{intent}.json
        master_db_code = master_db.code
        df_base_code = df_base.code
        deleted_new = master_db[~master_db_code.isin(df_base_code)]
        def mark_if_deleted(db):
            db["time of deletion"] = str(date)
            return db
        deleted_new = deleted_new.apply(mark_if_deleted, axis = 1)
        print(f"{deleted_new.shape[0]} listings have been deleted")
        if deleted_new.shape[0] > 0:
            try:
                deleted_db = pd.read_json(f"data/raw/deleted_{intent}.json")
                print(f"Found deleted_{intent}.json")
                deleted_db = pd.concat([deleted_db, deleted_new])
            except FileNotFoundError:
                print(f"No such file deleted_{intent}.json. Creating deleted_{intent}.json")
                deleted_db = deleted_new

            print(f"Saving deleted_{intent}.json")
            deleted_db.reset_index(drop=True, inplace=True)
            deleted_db.to_json(f"data/raw/deleted_{intent}.json")
            # Finally remove delete listings from master
            master_db = master_db[master_db_code.isin(df_base_code)]


        # Add new listings if there are some
        if len(new_ids) != 0:
            master_db = pd.concat([master_db, new_ids_complete])

    # Check if there are duplicates in master_db and raise error
    duplicates = master_db[master_db["code"].duplicated()].shape[0]
    if duplicates > 0:
        raise pd.errors.DuplicateLabelError(f"Found {duplicates} duplicated values")

    # Save to json
    print(f"Saving to {intent}.json")
    master_db.reset_index(drop=True, inplace=True)
    master_db.to_json(f"last_scraping_for_modeling/{intent}.json", index = False)
    # TODO: update from file and backup current file

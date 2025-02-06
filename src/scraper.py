"""
    Scraper for the project. Uses Sreality.cz for gathering the data.
    Run by calling run_online() (see run_online() description)
    Operates with sale.json and rent.json
"""

import requests # for making HTTP requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
import random

#------ SETTINGS ------
# How many details to be scraped per iteration. Most of the process time is spent on this.
# Lower number is safer as the listings are saved each iteration but is slower.
limit_for_details = 200

# If there is a need for more iterations of scraping, should the script call itself that many times?
recursion = True
# ---------------------


# Declare option to sale or to rent
intention = {
    "sale": 1,
    "rent": 2
}

# Get current date
date =  datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

# Use headers as Sreality.cz obfuscates prices
headers_user = {"User-Agent": "Mozilla/5.0"}


def get_sreality(category_type, category_main = 1, locality_region = 10):
    get_estates = lambda x : f"https://www.sreality.cz/api/v1/estates/search?category_main_cb={category_main}&category_type_cb={category_type}&locality_region_id={locality_region}&limit={x}"
    r_sleep = random.uniform(1.01, 1.81)
    time.sleep(r_sleep)

    total = requests.get(get_estates(1), headers = headers_user).json()["pagination"]["total"]

    print(f"Found {total} listings")

    try:
        r = requests.get(get_estates(total+1), headers = headers_user)
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
    "locality_seo": lambda: str(json_data["seo"]["locality"]),
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
    "has_details": lambda: int(1)
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
        "Balkón":"balcony_area",
        "Sklep":"cellar_area",
        "Lodžie" : "loggia_area",
        "Výtah": "elevator",
        "Energetická náročnost budovy": "energy_efficiency_rating",
        "Bezbariérový": "no_barriers",
        "Datum zahájení prodeje": "start_of_offer"
    }

    try:
        for item in json_data["items"]:
            if item["name"] in itemRenameTable:
                db[itemRenameTable[item["name"]]] = item["value"]
                del itemRenameTable[item["name"]]
    except KeyError:
        pass
    # Make sure all columns are filled either with data or NaN
    for item_left in itemRenameTable:
        db[itemRenameTable[item_left]] = np.nan
    # endregion

    return db


def get_all_sreality(category_type: int):


    json_data = get_sreality(category_type)
    if len(json_data['results']) == 0:
        raise LookupError("empty results, wrong api request")

    db = pd.DataFrame(json_data["results"])

    db.drop_duplicates(subset=["hash_id"], inplace=True)

    # Remove adverts costing 1 CZK
    db.drop(db[db.price <= 1].index, inplace=True)

    # Get first image from nested dict in _links
    db["image"] = db.advert_images.apply(lambda x: "https:" + x[0] + "?fl=res,400,300,3|shr,,20|jpg,90")

    # Add name of part of city and street for displaying purposes
    locality = pd.json_normalize(db["locality"])
    db["citypart"] = locality["citypart"]
    db["street"] = locality["street"]

    db["estimate"] = np.nan

    # Extract code and price
    db = db[["hash_id", "price_czk", "image", "citypart", "street", "estimate"]]

    # Change id to code as it will be used for matching
    db.rename(columns={'hash_id':'code', "price_czk": "price"}, inplace=True)
    db = db.convert_dtypes().reset_index(drop=True).dropna(subset=["code"])
    return db


def get_all_description(db):
    list_of_dfs = []

    def get_details_of_codes(codes):
        iteration = 1
        for code in list(codes):
            json_data = get_description(code)
            if len(json_data) == 1:
                continue  # Invalid code
            if iteration > 1:
                print("\r", end="")
            if iteration == limit_for_details+1:
                print("")
            print(f"Getting details ({iteration})", end="")
            list_of_dfs.append(convert_description_to_df(json_data))
            iteration += 1


    if db["code"].shape[0] > limit_for_details:
        required_runs = round((db["code"].shape[0] - limit_for_details)/limit_for_details)
        print(f"Sequential scraping required as there are too many details missing. Run me {required_runs} more times")
        get_details_of_codes(list(db["code"])[:limit_for_details])

        existing_cols = pd.concat(list_of_dfs).columns

    else:
        required_runs = 0
        get_details_of_codes(list(db["code"]))

    return pd.concat(list_of_dfs), required_runs


def clean(db):
    if db["has_details"] == 1:
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
        try:
            meta_desc = str(db["meta_description"])
            cat = meta_desc.split()[0].lower()
            if meta_desc.split()[1] == "atypické":
                intent = meta_desc.split()[6]
                size = "atypicky"
            elif meta_desc.split()[4] == "více":
                intent = meta_desc.split()[8]
                size = "6-a-vice"
            else:
                intent = meta_desc.split()[5]
                size = meta_desc.split()[1]

            correction_table = {
                "prodeji": "prodej",
                "pronájmu": "pronajem"
                }

            try:
                intent = correction_table[intent]
                db["link"] = f"https://www.sreality.cz/detail/{intent}/{cat}/{size}/{db["locality_seo"]}/{db["code"]}"
            except KeyError:
                print(meta_desc)
                db["link"] = np.nan
        except IndexError:
            db["link"] = np.nan

        # Add size as a column
        db["size"] = size

        # Add columns for matching deleted adverts
        db["time_of_deletion"] = np.nan

        # Add timestamp
        db["timestamp"] = date
    else:
        db["energy_efficiency_description"] = np.nan
        db["link"] = np.nan
        db["time_of_deletion"] =np.nan
        db["timestamp"] = np.nan
    return db


def parse(base, desc):
    db = pd.merge(base, desc, on='code')
    db = db.apply(clean, axis=1)
    db[["timestamp"]] = db[["timestamp"]].astype(str)
    return db


def run_online(intent):
    """
        Executes various functions to update sale.json or rent.json from Sreality.cz.
        :param intent: either "sale" or "rent"


        Works in this order: finds new listings and their details, finds and marks deleted listings,
        merges and saves to either sale.json or rent.json.
    """
    if intent not in ["sale", "rent"]:
        raise ValueError(f"""arg has to be either "sale" or "rent", not: {intent}""")

    cb_type = intention[intent]
    master_db = None

    # Check if sale.json or rent.json exist
    try:
        master_db = pd.read_json(f"last_scraping_for_modeling/{intent}.json")
        print(f"Found {intent}.json")
    except FileNotFoundError:
        print(f"No such file {intent}.json. No matching possible. Creating {intent}.json")
    print("Finding all listings from Sreality.cz")
    df_base = get_all_sreality(cb_type)

    if master_db is None:
        print(f"Starting scraping details of usable {df_base.shape[0]} listings")
        df_desc,req_runs = get_all_description(df_base)
        print("Found details of " + str(df_desc.shape[0]) + " listings")
        master_db = parse(df_base, df_desc)
    else:
        # Only find details for where they are missing
        new_ids = df_base[~df_base["code"].isin(master_db["code"])]
        print(f"Found {new_ids.shape[0]} new listings")
        print("Getting their details")
        if len(new_ids) != 0:
            new_ids_desc,req_runs = get_all_description(new_ids)
            new_ids_complete = parse(new_ids, new_ids_desc)
        else:
            req_runs = 0

        # Check for deleted listings and save them to deleted_{intent}.json
        master_db_code = master_db.code
        df_base_code = df_base.code
        deleted_new = master_db[~master_db_code.isin(df_base_code)]
        def mark_if_deleted(db):
            db["time_of_deletion"] = str(date)
            db[["time_of_deletion"]] = db[["time_of_deletion"]].astype(str)
            return db
        deleted_new = deleted_new.apply(mark_if_deleted, axis = 1)
        print(f"{deleted_new.shape[0]} listings have been deleted")
        if deleted_new.shape[0] > 0:
            deleted_new[["time_of_deletion"]] =  deleted_new[["time_of_deletion"]].astype(str)
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

    # Delete rows with NAs in code column
    master_db.dropna(subset="code", inplace=True)

    # Check if there are duplicates in master_db and raise error
    duplicates = master_db[master_db["code"].duplicated()].shape[0]
    if duplicates > 0:
        raise pd.errors.DuplicateLabelError(f"Found {duplicates} duplicated values")

    # Update prices
    print("Updating prices")
    updated_prices = df_base[["code", "price"]]
    updated_prices.set_index("code", inplace=True)
    master_db_mod = master_db.set_index('code')
    master_db_mod.update(updated_prices, overwrite=True)
    master_db = master_db_mod.reset_index()

    # Save to json
    print(f"Saving to {intent}.json")
    master_db.reset_index(drop=True, inplace=True)
    master_db[["timestamp"]] = master_db[["timestamp"]].astype(str)
    master_db.to_json(f"last_scraping_for_modeling/{intent}.json", index = False)
    print("Scraping complete")
    if req_runs > 0:
        print(f"Scraped data is incomplete, please run scraper {req_runs} more times")
        if recursion:
            print("Running scraper again")
            run_online(intent)
    else:
        print("Scraped data is complete as of now, no need to run scraper again")

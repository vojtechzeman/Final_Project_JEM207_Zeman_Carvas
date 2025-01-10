import json
import csv
import pandas as pd
import re


class DataProcessor:
    def __init__(self) -> None:
        pass

    def process_data(self, process_sale: bool = False, process_rent: bool = False) -> None:
        """
        price
        usable_area (missing values got from meta_description, if usable_area > floor_area, exchange them)
        garage
        cellar
        low_energy (nizkoenergetický)
        balcony
        easy_access (no barriers)
        terrace
        loggia
        parking_lots
        date (timestamp to date)
        elevator (got from meta_description)
        material_brick
        material_panel
        Prague_1 (find missing districts using Prague_street_database.csv)
        Prague_2
        Prague_3
        Prague_4
        Prague_5
        Prague_6
        Prague_7
        Prague_8
        Prague_9
        floor_ground
        floor_above_ground
        status_good (dobrý, špatný, k demolici)
        status_very_good
        status_before_reconstruction (před rekonstrukcí, v rekonstrukci)
        status_after_reconstruction
        status_project
        status_under_construction
        kitchen_separately (+1 vs +kk)
        ownership_private
        non-residential_unit (description contains "nebyt|nebytu|nebytový|ateli[eé]r")

        RENT:
        furnished
        ownership_private - deleted
        status_before_reconstruction - deleted
        status_project - deleted
        status_under_construction - deleted

        """

        if not process_sale and not process_rent:
            return

        if process_sale and process_rent:
            raise ValueError("Only one of process_sale or process_rent can be True")

        # Load JSON
        if process_sale:
            with open("data/raw/deleted_listings_sale.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
        elif process_rent:
            with open("data/raw/deleted_listings_rent.json", 'r', encoding='utf-8') as file:
                data = json.load(file)

        # Load prices from CSV
        prices = {}
        if process_sale:
            with open("data/raw/deleted_listings_sale.csv", 'r', encoding='utf-8') as file:
                next(file)  # Skip header
                csv_reader = csv.reader(file, delimiter=';')
                for row in csv_reader:
                    code, price, _ = row  # _ ignores timestamp
                    prices[code] = int(price)
        elif process_rent:
            with open("data/raw/deleted_listings_rent.csv", 'r', encoding='utf-8') as file:
                next(file)  # Skip header
                csv_reader = csv.reader(file, delimiter=';')
                for row in csv_reader:
                    code, price, _ = row  # _ ignores timestamp
                    prices[code] = int(price)

        # Add prices to data
        for item in data:
            if 'code' in item and str(item['code']) in prices:
                item['price'] = prices[str(item['code'])]

        # Remove unnecessary keys
        KEYS_TO_REMOVE = {
            "basin",
            "broker_company",
            "broker_id",
            "building_condition",
            "building_type",
            "category_main_cb",
            "category_type_cb",
            "id_of_order",
            "last_update",
            "locality_country_id",
            "locality_gps_lat",
            "locality_gps_lon",
            "locality_region_id",
            "no_barriers",
            "note_about_price",
            "ownership_type",
            "room_count_cb",
            "start_of_offer",
            "locality_municipality_id",
            "locality_quarter_id",
            "locality_street_id",
            "locality_ward_id",
            "object_kind",
            "object_type",
            "energy_efficiency_rating_cb",
            "code"
        }

        cleaned_data = [{k: v for k, v in item.items() if k not in KEYS_TO_REMOVE} for item in data]
        if process_sale:
            cleaned_data = [{k: v for k, v in item.items() if k != "furnished"} for item in cleaned_data]
        if process_rent:
            cleaned_data = [{k: v for k, v in item.items() if k != "ownership"} for item in cleaned_data]



        # Delete items with "price": 1
        cleaned_data = [item for item in cleaned_data if item["price"] != 1]


        # Process data
        print("Processing...")
        for item in cleaned_data:
            # Convert timestamp to date
            item['date'] = item['timestamp'].split()[0]
            del item['timestamp']

            # Missing usable_area data
            try:
                if item['meta_description'].split()[2] == "pokojů":
                    item['usable_area'] = int(float(item['meta_description'].split()[5]))
                elif item['meta_description'].split()[2] == "dispozice":
                    item['usable_area'] = int(float(item['meta_description'].split()[3]))
                else:
                    item['usable_area'] = int(float(item['meta_description'].split()[2]))
            except (ValueError, IndexError):
                item['usable_area'] = None
                

            # Exchange of usable_area and floor_area
            if item['floor_area'] is not None:
                try:
                    floor_area = int(float(item['floor_area']))
                    if item['usable_area'] > floor_area:
                        item['usable_area'], item['floor_area'] = floor_area, item['usable_area']
                    item['floor_area'] = floor_area
                except ValueError:
                    item['floor_area'] = None

            # Completion of missing locality_district_id
            streets = pd.read_csv("Prague_street_database.csv", encoding='windows-1250', delimiter=';')
            if item["locality_district_id"] not in [5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010]:
                if ";" not in item["meta_description"].split(",")[0]:
                    text = item["meta_description"].split(",")[0]
                    text = text.split()
                    if process_sale:
                        ulice = text[text.index("prodeji") + 1:]
                    elif process_rent:
                        ulice = text[text.index("pronájmu") + 1:]
                    ulice = " ".join(ulice)
                    
                    # Find the street name in the database
                    matching_row = streets[streets['Název ulice'] == ulice]
                    if len(matching_row) > 0:
                        district = matching_row['Název obvodu Prahy'].iloc[0]
                        item["locality_district_id"] = int(district.split()[1]) + 5000
                else:
                    cleaned_data.remove(item)

        print("Processing...")
        for item in cleaned_data:
            # Elevator dummy
            if "výtah" in item["meta_description"]:
                item["elevator"] = 1
            else:
                item["elevator"] = 0
                        
            # Remove unnecessary keys
            del item['meta_description']


        # Delete NAs in usable_area
        cleaned_data = [item for item in cleaned_data if item["usable_area"] is not None]
        # Delete floor_area
        cleaned_data = [{k: v for k, v in item.items() if k != "floor_area"} for item in cleaned_data]



        print("Processing...")
        for item in cleaned_data:
            # Material dummy (cihlová, panelová, ostatní)
            if item["material"] == "Cihlová":
                item["material_brick"] = 1
            else:
                item["material_brick"] = 0
            if item["material"] == "Panelová":
                item["material_panel"] = 1
            else:
                item["material_panel"] = 0
            del item['material']

            # Locality_district_id dummy (Prague 1-10)
            if item["locality_district_id"] == 5001:
                item["Prague_1"] = 1
            else:
                item["Prague_1"] = 0
            if item["locality_district_id"] == 5002:
                item["Prague_2"] = 1
            else:
                item["Prague_2"] = 0
            if item["locality_district_id"] == 5003:
                item["Prague_3"] = 1
            else:
                item["Prague_3"] = 0
            if item["locality_district_id"] == 5004:
                item["Prague_4"] = 1
            else:
                item["Prague_4"] = 0
            if item["locality_district_id"] == 5005:
                item["Prague_5"] = 1
            else:
                item["Prague_5"] = 0
            if item["locality_district_id"] == 5006:
                item["Prague_6"] = 1
            else:
                item["Prague_6"] = 0
            if item["locality_district_id"] == 5007:
                item["Prague_7"] = 1
            else:
                item["Prague_7"] = 0
            if item["locality_district_id"] == 5008:
                item["Prague_8"] = 1
            else:
                item["Prague_8"] = 0
            if item["locality_district_id"] == 5009:
                item["Prague_9"] = 1
            else:
                item["Prague_9"] = 0
            del item['locality_district_id']

            # Easy_access NA and FALSE merge
            if item["easy_access"] == 2:
                item["easy_access"] = 0

        print("Processing...")
        for item in cleaned_data:
            # Floor dummy (přízemí, nadzemí, podzemí)
            floor = item["floor"].split()[0].split(".")[0]
            item["floor"] = floor if "p" not in floor else "1"

            if item["floor"] == "1" or item["floor"] == "přízemí":
                item["floor_ground"] = 1
            else:
                item["floor_ground"] = 0
            if int(item["floor"]) > 1:
                item["floor_above_ground"] = 1
            else:
                item["floor_above_ground"] = 0
            del item['floor']

            # Condition dummy (dobrý, velmi dobrý, před rekonstrukcí, po rekonstrukci, projekt, ve výstavbě, novostavba)
            if process_sale:
                if item["age_of_building"] in ["Dobrý", "Špatný", "K demolici"]:
                    item["status_good"] = 1
                else:
                    item["status_good"] = 0

                if item["age_of_building"] == "Velmi dobrý":
                    item["status_very_good"] = 1
                else:
                    item["status_very_good"] = 0

                if item["age_of_building"] in ["Před rekonstrukcí", "V rekonstrukci"]:
                    item["status_before_reconstruction"] = 1
                else:
                    item["status_before_reconstruction"] = 0
                
                if item["age_of_building"] == "Po rekonstrukci":
                    item["status_after_reconstruction"] = 1
                else:
                    item["status_after_reconstruction"] = 0

                if item["age_of_building"] == "Projekt":
                    item["status_project"] = 1
                else:
                    item["status_project"] = 0
                
                if item["age_of_building"] == "Ve výstavbě":
                    item["status_under_construction"] = 1
                else:
                    item["status_under_construction"] = 0

                del item['age_of_building']

            # Condition dummy (dobrý, velmi dobrý, po rekonstrukci, novostavba)
            if process_rent:
                if item["age_of_building"] in ["Dobrý", "Špatný", "K demolici", "Před rekonstrukcí"]:
                    item["status_good"] = 1
                else:
                    item["status_good"] = 0

                if item["age_of_building"] == "Velmi dobrý":
                    item["status_very_good"] = 1
                else:
                    item["status_very_good"] = 0

                if item["age_of_building"] in ["Po rekonstrukci", "V rekonstrukci"]:
                    item["status_after_reconstruction"] = 1
                else:
                    item["status_after_reconstruction"] = 0

                del item['age_of_building']


        print("Processing...")
        for item in cleaned_data:

            # Kitchen_separately dummy 
            if item["category_sub_cb"] in [3, 5, 7, 9, 11]:
                item["kitchen_separately"] = 1
            else:
                item["kitchen_separately"] = 0
            del item['category_sub_cb']

            # Ownership_private dummy
            if process_sale:
                if item["ownership"] in [1, 3]:
                    item["ownership_private"] = 1
                else:
                    item["ownership_private"] = 0

            # nebytová jednotka
            if re.search(r"nebyt|nebytu|nebytový|ateli[eé]r", item["description"].lower()):
                item["nonresidential_unit"] = 1
            else:
                item["nonresidential_unit"] = 0

            # Furnished dummy
            if process_rent:
                if item["furnished"] == 1:
                    item["fully_furnished"] = 1
                else:
                    item["fully_furnished"] = 0

                if item["furnished"] == 3:
                    item["partially_furnished"] = 1
                else:
                    item["partially_furnished"] = 0
                
                del item['furnished']


        # Delete date
        cleaned_data = [{k: v for k, v in item.items() if k != "date"} for item in cleaned_data]

        # Delete description
        if process_rent:
            cleaned_data = [{k: v for k, v in item.items() if k != "description"} for item in cleaned_data]
            cleaned_data = [{k: v for k, v in item.items() if k != "timestamp"} for item in cleaned_data]


        # Save result
        if process_sale:
            with open("data/processed/sale.json", 'w', encoding='utf-8') as file:
                json.dump(cleaned_data, file, indent=2, ensure_ascii=False)
        elif process_rent:
            df = pd.DataFrame(cleaned_data)
            desired_order = ['price', 'usable_area']
            other_columns = [col for col in df.columns if col not in desired_order]
            final_order = desired_order + other_columns
            df = df[final_order]
            df.to_csv("data/processed/rent.csv", index=False, encoding='utf-8', sep=";")



        print(f"Successfully processed data")


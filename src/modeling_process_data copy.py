import json
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

        # Load JSON data
        file_path = "data/raw/deleted_listings_sale.json" if process_sale else "data/raw/deleted_listings_rent.json"
        with open(file_path, 'r', encoding='utf-8') as file:
            data = pd.DataFrame(json.load(file))

        # Load prices from CSV
        csv_path = "data/raw/deleted_listings_sale.csv" if process_sale else "data/raw/deleted_listings_rent.csv"
        prices_df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
        prices_df.columns = ['code', 'price', 'timestamp']
        prices_df['code'] = prices_df['code'].astype(str)
        
        # Merge prices with main data
        data['code'] = data['code'].astype(str)
        data = pd.merge(data, prices_df[['code', 'price']], on='code', how='left')

        # Remove unnecessary columns
        columns_to_remove = [
            "basin", "broker_company", "broker_id", "building_condition", "building_type",
            "category_main_cb", "category_type_cb", "id_of_order", "last_update",
            "locality_country_id", "locality_gps_lat", "locality_gps_lon", "locality_region_id",
            "no_barriers", "note_about_price", "ownership_type", "room_count_cb",
            "start_of_offer", "locality_municipality_id", "locality_quarter_id",
            "locality_street_id", "locality_ward_id", "object_kind", "object_type",
            "energy_efficiency_rating_cb", "code"
        ]
        data = data.drop(columns=[col for col in columns_to_remove if col in data.columns])

        # Remove specific columns based on process type
        if process_sale:
            data = data.drop(columns=['furnished'], errors='ignore')
        if process_rent:
            data = data.drop(columns=['ownership'], errors='ignore')

        # Remove rows with price = 1
        data = data[data['price'] != 1]

        # Process date
        data['date'] = pd.to_datetime(data['timestamp']).dt.date
        data = data.drop(columns=['timestamp'])

        # Process usable area
        def extract_usable_area(desc):
            try:
                words = desc.split()
                if words[2] == "pokojů":
                    return float(words[5])
                elif words[2] == "dispozice":
                    return float(words[3])
                else:
                    return float(words[2])
            except (ValueError, IndexError):
                return None

        data['usable_area'] = data['meta_description'].apply(extract_usable_area)

        # Handle floor area exchange
        mask = (data['floor_area'].notna()) & (data['usable_area'] > data['floor_area'])
        data.loc[mask, ['usable_area', 'floor_area']] = data.loc[mask, ['floor_area', 'usable_area']].values

        # Process district information
        streets = pd.read_csv("Prague_street_database.csv", encoding='windows-1250', delimiter=';')
        
        def get_district_id(row):
            if row['locality_district_id'] in range(5001, 5011):
                return row['locality_district_id']
            
            try:
                text = row['meta_description'].split(',')[0]
                if ";" in text:
                    return None
                
                words = text.split()
                keyword = "prodeji" if process_sale else "pronájmu"
                street_name = " ".join(words[words.index(keyword) + 1:])
                
                matching_district = streets[streets['Název ulice'] == street_name]['Název obvodu Prahy'].iloc[0]
                return int(matching_district.split()[1]) + 5000
            except (ValueError, IndexError):
                return None

        data['locality_district_id'] = data.apply(get_district_id, axis=1)
        data = data.dropna(subset=['locality_district_id'])

        # Process elevator
        data['elevator'] = data['meta_description'].str.contains('výtah').astype(int)
        data = data.drop(columns=['meta_description'])

        # Remove rows with missing usable_area and floor_area
        data = data.dropna(subset=['usable_area'])
        data = data.drop(columns=['floor_area'])

        # Process material
        data['material_brick'] = (data['material'] == 'Cihlová').astype(int)
        data['material_panel'] = (data['material'] == 'Panelová').astype(int)
        data = data.drop(columns=['material'])

        # Process district dummies
        for i in range(1, 10):
            data[f'Prague_{i}'] = (data['locality_district_id'] == 5000 + i).astype(int)
        data = data.drop(columns=['locality_district_id'])

        # Process easy access
        data['easy_access'] = data['easy_access'].replace(2, 0)

        # Process floor information
        def process_floor(floor_str):
            floor = floor_str.split()[0].split('.')[0]
            return '1' if 'p' in floor else floor

        data['floor'] = data['floor'].apply(process_floor)
        data['floor_ground'] = (data['floor'].isin(['1', 'přízemí'])).astype(int)
        data['floor_above_ground'] = (data['floor'].astype(int) > 1).astype(int)
        data = data.drop(columns=['floor'])

        # Process building age/condition
        if process_sale:
            status_mappings = {
                'status_good': ['Dobrý', 'Špatný', 'K demolici'],
                'status_very_good': ['Velmi dobrý'],
                'status_before_reconstruction': ['Před rekonstrukcí', 'V rekonstrukci'],
                'status_after_reconstruction': ['Po rekonstrukci'],
                'status_project': ['Projekt'],
                'status_under_construction': ['Ve výstavbě']
            }
        else:
            status_mappings = {
                'status_good': ['Dobrý', 'Špatný', 'K demolici', 'Před rekonstrukcí'],
                'status_very_good': ['Velmi dobrý'],
                'status_after_reconstruction': ['Po rekonstrukci', 'V rekonstrukci']
            }

        for status, values in status_mappings.items():
            data[status] = data['age_of_building'].isin(values).astype(int)
        data = data.drop(columns=['age_of_building'])

        # Process kitchen type
        data['kitchen_separately'] = data['category_sub_cb'].isin([3, 5, 7, 9, 11]).astype(int)
        data = data.drop(columns=['category_sub_cb'])

        # Process ownership if sale
        if process_sale:
            data['ownership_private'] = data['ownership'].isin([1, 3]).astype(int)

        # Process non-residential unit
        data['nonresidential_unit'] = data['description'].str.lower().str.contains(
            r'nebyt|nebytu|nebytový|ateli[eé]r'
        ).astype(int)

        # Process furnished if rent
        if process_rent:
            data['fully_furnished'] = (data['furnished'] == 1).astype(int)
            data['partially_furnished'] = (data['furnished'] == 3).astype(int)
            data = data.drop(columns=['furnished'])

        # Final cleanup
        data = data.drop(columns=['date'])
        if process_rent:
            data = data.drop(columns=['description', 'timestamp'], errors='ignore')

        # Save processed data
        if process_sale:
            data.to_json("data/processed/sale.json", orient='records', indent=2, force_ascii=False)
        else:
            # Reorder columns for rent data
            first_cols = ['price', 'usable_area']
            other_cols = [col for col in data.columns if col not in first_cols]
            data = data[first_cols + other_cols]
            data.to_csv("data/processed/rent.csv", index=False, encoding='utf-8', sep=";")

        print(f"Successfully processed data")
import json
import csv
import pandas as pd
import re


class DataProcessor:
    def __init__(self) -> None:
        self.streets_df = pd.read_csv("Prague_street_database.csv", encoding='windows-1250', delimiter=';')
        
        # Columns we work with
        self.keep_columns = {
            'garage', 'floor_area', 'category_sub_cb', 'ownership', 
            'cellar', 'locality_district_id', 'furnished', 'low_energy', 
            'floor', 'balcony', 'usable_area', 'easy_access', 
            'description', 'material', 'age_of_building', 
            'meta_description', 'terrace', 'loggia', 'parking_lots', 'price'
        }

    def process_data(self, process_sale: bool = False, process_rent: bool = False) -> None:
        """
        SALE:

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
        furnished - added
        ownership_private - deleted
        status_before_reconstruction - deleted
        status_project - deleted
        status_under_construction - deleted

        """

        # Load raw JSON data
        if process_sale:
            df = pd.read_json("data/raw/deleted_sale.json")
        elif process_rent:
            df = pd.read_json("data/raw/deleted_rent.json")
            
        # Keep only specified columns
        df = df[[col for col in df.columns if col in self.keep_columns]]
        

        # Remove specific columns based on process type
        if process_sale:
            df = df.drop(columns=['furnished'], errors='ignore')
        if process_rent:
            df = df.drop(columns=['ownership'], errors='ignore')

        # Remove rows where price is 1 or 0 or NA
        df = df.dropna(subset=['price'])
        df = df[df['price'] != 0]
        df = df[df['price'] != 1]

        # Process usable area from meta_description
        def extract_usable_area(desc):
            try:
                words = desc.split()
                if words[2] == "pokojů":
                    return int(float(words[5]))
                elif words[2] == "dispozice":
                    return int(float(words[3]))
                else:
                    return int(float(words[2]))
            except (ValueError, IndexError):
                return None

        df['usable_area'] = df['meta_description'].apply(extract_usable_area)

        # Exchange usable_area and floor_area where necessary
        df['floor_area'] = pd.to_numeric(df['floor_area'], errors='coerce')
        mask = (df['usable_area'] > df['floor_area']) & df['floor_area'].notna()
        df.loc[mask, ['usable_area', 'floor_area']] = df.loc[mask, ['floor_area', 'usable_area']].values
        df = df.dropna(subset=['usable_area'])

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
                search_term = "prodeji" if process_sale else "pronájmu"
                idx = words.index(search_term) + 1
                street_name = " ".join(words[idx:])
                
                matching_row = streets[streets['Název ulice'] == street_name]
                if not matching_row.empty:
                    district_num = int(matching_row['Název obvodu Prahy'].iloc[0].split()[1])
                    return district_num + 5000
            except (ValueError, IndexError):
                pass
            return None

        df['locality_district_id'] = df.apply(get_district_id, axis=1)
        df = df.dropna(subset=['locality_district_id'])

        # Add elevator dummy
        df['elevator'] = df['meta_description'].str.contains('výtah').astype(int)
        
        # Remove meta_description
        df = df.drop(columns=['meta_description'])

        # Remove rows with NA in usable_area and drop floor_area
        df = df.dropna(subset=['usable_area'])
        df = df.drop(columns=['floor_area'])

        # Process material dummies
        df['material_brick'] = (df['material'] == 'Cihlová').astype(int)
        df['material_panel'] = (df['material'] == 'Panelová').astype(int)
        df = df.drop(columns=['material'])

        # Process district dummies
        for i in range(1, 10):
            df[f'Prague_{i}'] = (df['locality_district_id'] == 5000 + i).astype(int)
        df = df.drop(columns=['locality_district_id'])

        # Process easy_access
        df['easy_access'] = df['easy_access'].replace(2, 0)

        # Process floor information
        def process_floor(floor_str):
            floor = floor_str.split()[0].split('.')[0]
            return '1' if 'p' in floor else floor

        df['floor'] = df['floor'].apply(process_floor)
        df['floor_ground'] = ((df['floor'] == '1') | (df['floor'] == 'přízemí')).astype(int)
        df['floor_above_ground'] = (pd.to_numeric(df['floor'], errors='coerce') > 1).astype(int)
        df = df.drop(columns=['floor'])

        # Process building age status
        if process_sale:
            df['status_good'] = df['age_of_building'].isin(['Dobrý', 'Špatný', 'K demolici']).astype(int)
            df['status_very_good'] = (df['age_of_building'] == 'Velmi dobrý').astype(int)
            df['status_before_reconstruction'] = df['age_of_building'].isin(['Před rekonstrukcí', 'V rekonstrukci']).astype(int)
            df['status_after_reconstruction'] = (df['age_of_building'] == 'Po rekonstrukci').astype(int)
            df['status_project'] = (df['age_of_building'] == 'Projekt').astype(int)
            df['status_under_construction'] = (df['age_of_building'] == 'Ve výstavbě').astype(int)
        elif process_rent:
            df['status_good'] = df['age_of_building'].isin(['Dobrý', 'Špatný', 'K demolici', 'Před rekonstrukcí']).astype(int)
            df['status_very_good'] = (df['age_of_building'] == 'Velmi dobrý').astype(int)
            df['status_after_reconstruction'] = df['age_of_building'].isin(['Po rekonstrukci', 'V rekonstrukci']).astype(int)
        
        df = df.drop(columns=['age_of_building'])

        # Process kitchen separately
        df['kitchen_separately'] = df['category_sub_cb'].isin([3, 5, 7, 9, 11]).astype(int)
        df = df.drop(columns=['category_sub_cb'])

        # Process ownership and non-residential unit
        if process_sale:
            df['ownership_private'] = df['ownership'].isin([1, 3]).astype(int)
            
        df['nonresidential_unit'] = df['description'].str.contains(
            r"nebyt|nebytu|nebytový|ateli[eé]r", 
            case=False, 
            regex=True
        ).astype(int)

        # Process furnished status for rentals
        if process_rent:
            df['fully_furnished'] = (df['furnished'] == 1).astype(int)
            df['partially_furnished'] = (df['furnished'] == 3).astype(int)
            df = df.drop(columns=['furnished'])

        # Replace NA's by 0's
        df = df.fillna(0)

        # Final cleanup
        if process_rent:
            df = df.drop(columns=['description'], errors='ignore')
            # Reorder columns
            cols = ['price', 'usable_area'] + [col for col in df.columns if col not in ['price', 'usable_area']]
            df = df[cols]
            # Save as CSV
            df.to_csv("data/processed/rent.csv", index=False, encoding='utf-8', sep=";")
        else:
            # Save as JSON
            df.to_json("data/processed/sale.json", orient='records', force_ascii=False, indent=2)

        print(f"Successfully processed data")


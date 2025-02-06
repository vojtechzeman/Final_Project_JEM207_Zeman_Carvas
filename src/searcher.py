from sklearn.pipeline import Pipeline
import joblib
import pandas as pd
import os


class Searcher:
    def __init__(self) -> None:
        pass

    def load_model(self, load_sale: bool = False, load_rent: bool = False) -> Pipeline:
        if load_sale:
            model = joblib.load("sale_model.joblib")
        elif load_rent:
            model = joblib.load("rent_model.joblib")
        return model

    def search_apartments(self, process_sale: bool = False, process_rent: bool = False) -> pd.DataFrame:

        # Load data
        if process_sale:
            df = pd.read_json("data/processed/sale.json")
            os.remove("data/processed/sale.json")
        elif process_rent:
            df = pd.read_json("data/processed/rent.json")
            os.remove("data/processed/rent.json")


        # Split features
        continuous_features = ['usable_area']
        if process_sale:
            dummy_features = [
                'garage', 'cellar', 'low_energy', 'balcony', 'easy_access',
                'terrace', 'loggia', 'parking_lots', 'elevator', 'material_brick',
                'material_panel', 'Prague_1', 'Prague_2', 'Prague_3', 'Prague_4',
                'Prague_5', 'Prague_6', 'Prague_7', 'Prague_8', 'Prague_9',
                'floor_ground', 'floor_above_ground', 'status_good', 'status_very_good',
                'status_before_reconstruction', 'status_after_reconstruction',
                'status_project', 'status_under_construction', 'kitchen_separately',
                'ownership_private', 'nonresidential_unit'
            ]
        elif process_rent:
            dummy_features = [
                'garage', 'cellar', 'low_energy', 'balcony', 'easy_access',
                'terrace', 'loggia', 'parking_lots', 'elevator', 'material_brick',
                'material_panel', 'Prague_1', 'Prague_2', 'Prague_3', 'Prague_4',
                'Prague_5', 'Prague_6', 'Prague_7', 'Prague_8', 'Prague_9',
                'floor_ground', 'floor_above_ground', 'status_good', 'status_very_good',
                'status_after_reconstruction', 'kitchen_separately', 'nonresidential_unit',
                'fully_furnished', 'partially_furnished'
            ]

        # Load model
        model = self.load_model(load_sale=process_sale, load_rent=process_rent)

        # Make predictions
        predicted_prices = model.predict(df[continuous_features + dummy_features])

        # Create output DataFrame
        result_df = pd.DataFrame({
            'code': df.index,
            'predicted_price': predicted_prices
        })
        

        return result_df


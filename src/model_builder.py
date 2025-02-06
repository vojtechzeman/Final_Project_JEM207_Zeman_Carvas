import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os


class Model:
    def __init__(self) -> None:
        pass

    def train_model(self, process_sale: bool = False, process_rent: bool = False) -> None:
        # Load data
        if process_sale:
            df_0 = pd.read_csv("data/processed/sale_0.csv", sep=';')    # This is a dataset (scraped by different scraper) between September 2024 and January 2025. It is not included in datasets scraped by current scraper. In the future, when the current datasets are large enough, this dataset will be deleted.
            df = pd.read_csv("data/processed/sale.csv", sep=';')
        elif process_rent:
            df_0 = pd.read_csv("data/processed/rent_0.csv", sep=';')    # This is a dataset (scraped by different scraper) between September 2024 and January 2025. It is not included in datasets scraped by current scraper. In the future, when the current datasets are large enough, this dataset will be deleted.
            df = pd.read_csv("data/processed/rent.csv", sep=';')


        # Concatenate the datasets
        df = pd.concat([df_0, df], axis=0, ignore_index=True)
        
        
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
        
        # Base dataset
        X = df[continuous_features + dummy_features].copy()
        y = df['price'].copy()
        
        # Prepare preprocessor
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), continuous_features),
                ('cat', 'passthrough', dummy_features)
            ],
            sparse_threshold=0
        )
        
        # Model pipeline
        model = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', LinearRegression())
        ])
        
        # Train the model
        model.fit(X, y)

        print(f"Model successfully trained.")
    

        if process_sale:
            joblib.dump(model, "sale_model.joblib")
        elif process_rent:
            joblib.dump(model, "rent_model.joblib")  





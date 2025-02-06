import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from datetime import datetime
import glob
import joblib
import os


class Model:
    def __init__(self) -> None:
        pass

    def remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove outliers based on price per m² and extreme values.
        Uses IQR method as it's robust and doesn't assume normal distribution.
        """
        initial_len = len(df)
        
        # Calculate price per m²
        df['price_per_m2'] = df['price'] / df['usable_area']
        
        # IQR method for price per m²
        Q1_price = df['price_per_m2'].quantile(0.25)
        Q3_price = df['price_per_m2'].quantile(0.75)
        IQR_price = Q3_price - Q1_price
        price_lower = Q1_price - 1.5 * IQR_price
        price_upper = Q3_price + 1.5 * IQR_price
        
        # Remove price per m² outliers
        df = df[
            (df['price_per_m2'] >= price_lower) & 
            (df['price_per_m2'] <= price_upper)
        ]
        
        # Also remove extreme area values
        Q1_area = df['usable_area'].quantile(0.25)
        Q3_area = df['usable_area'].quantile(0.75)
        IQR_area = Q3_area - Q1_area
        area_lower = Q1_area - 1.5 * IQR_area
        area_upper = Q3_area + 1.5 * IQR_area
        
        df = df[
            (df['usable_area'] >= area_lower) & 
            (df['usable_area'] <= area_upper)
        ]
        
        return df

    def prepare_features(self, df: pd.DataFrame, dummy_features: list) -> pd.DataFrame:
        """
        Create interaction terms between area and dummy variables
        """
        # Create interactions for all dummy features
        area = df['usable_area']
        for feature in dummy_features:
            df[f'{feature}_x_area'] = df[feature] * area
        
        return df

    def train_model(self, process_sale: bool = False, process_rent: bool = False) -> None:
        """
        Train the real estate price prediction model with area interactions.
        """
        # Load data
        if process_sale:
            df_0 = pd.read_csv("data/processed/sale_0.csv", sep=';')
            df = pd.read_csv("data/processed/sale.csv", sep=';')
        elif process_rent:
            df_0 = pd.read_csv("data/processed/rent_0.csv", sep=';')
            df = pd.read_csv("data/processed/rent.csv", sep=';')

        # Concatenate the datasets
        df = pd.concat([df_0, df], axis=0, ignore_index=True)
        
        
        # Remove outliers
        df = self.remove_outliers(df)
        
        # Define base features
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

        # Create interaction features
        df = self.prepare_features(df, dummy_features)
        interaction_features = [f'{feature}_x_area' for feature in dummy_features]


        # Base dataset with interactions
        X = df[continuous_features + dummy_features + interaction_features].copy()
        y = df['price'].copy()
  
        # Model pipeline without scaling for direct coefficient interpretation
        preprocessor = ColumnTransformer(
            transformers=[
                ('all', 'passthrough', continuous_features + dummy_features + interaction_features)
            ],
            sparse_threshold=0
        )

        model = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', LinearRegression())
        ])


        # Train the model
        model.fit(X, y)


        print(f"\nModel successfully trained.")

        # Get current date in the desired format
        current_date = datetime.now().strftime("%d.%m.%Y")

        # Save the model
        if process_sale:
            os.remove(glob.glob("sale_model_*.joblib")[0])
            joblib.dump(model, f"sale_model_{current_date}.joblib")
        elif process_rent:
            os.remove(glob.glob("rent_model_*.joblib")[0])
            joblib.dump(model, f"rent_model_{current_date}.joblib")


    def load_model(self, load_sale: bool = False, load_rent: bool = False) -> Pipeline:
        """Load the most recent model file."""
        try:
            if load_sale:
                model = joblib.load(glob.glob("sale_model_*.joblib")[0])
            elif load_rent:
                model = joblib.load(glob.glob("rent_model_*.joblib")[0])
            return model
        except IndexError:
            raise FileNotFoundError("No model file found")
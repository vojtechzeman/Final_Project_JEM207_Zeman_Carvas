from sklearn.pipeline import Pipeline
import joblib


class Searcher:
    def __init__(self) -> None:
        pass

    def load_model(self, load_sale: bool = False, load_rent: bool = False) -> Pipeline:
        if load_sale:
            model = joblib.load("sale_model.joblib")
        elif load_rent:
            model = joblib.load("rent_model.joblib")




# import pandas as pd
# import joblib

# # Load your saved model
# model = joblib.load("rent_model.joblib")  # or "sale_model.joblib" depending on what you're predicting

# # Read your CSV
# df = pd.read_csv('your_file.csv', sep=';')

# # Create X with the same features used in training
# continuous_features = ['usable_area']
# dummy_features = [
#     'garage', 'cellar', 'low_energy', 'balcony', 'easy_access',
#     'terrace', 'loggia', 'parking_lots', 'elevator', 'material_brick',
#     'material_panel', 'Prague_1', 'Prague_2', 'Prague_3', 'Prague_4',
#     'Prague_5', 'Prague_6', 'Prague_7', 'Prague_8', 'Prague_9',
#     'floor_ground', 'floor_above_ground', 'status_good', 'status_very_good',
#     'status_after_reconstruction', 'kitchen_separately', 'nonresidential_unit',
#     'fully_furnished', 'partially_furnished'
# ]

# X = df[continuous_features + dummy_features]

# # Make predictions
# predicted_prices = model.predict(X)

# # Add predictions to the dataframe
# df['predicted_price'] = predicted_prices

# # Save the updated dataframe
# df.to_csv('your_file_with_predictions.csv', sep=';', index=False)
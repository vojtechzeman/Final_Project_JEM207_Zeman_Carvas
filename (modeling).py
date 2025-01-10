import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def evaluate_model(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    print("\nModel Performance Metrics:")
    print(f"R² Score: {r2:.4f}")
    print(f"RMSE: {rmse:,.0f}")
    print(f"MAE: {mae:,.0f}")
    print(f"MAPE: {mape:.2f}%")
    return {'r2': r2, 'rmse': rmse, 'mae': mae, 'mape': mape}

def prepare_data(input_file):
    # Load data
    df = pd.read_csv(input_file, sep=';')
    
    # Split features
    continuous_features = ['usable_area']
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
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return (X_train, X_test, y_train, y_test), continuous_features, dummy_features

def train_model(input_file='rent.csv'):
    (X_train, X_test, y_train, y_test), cont_features, other_features = prepare_data(input_file)
    
    # Prepare preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), cont_features),
            ('cat', 'passthrough', other_features)
        ],
        sparse_threshold=0
    )
    
    # Model pipeline
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Predictions and evaluation
    predictions = model.predict(X_test)
    metrics = evaluate_model(y_test, predictions)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    print(f"\nCross-validation R² scores: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Feature importance
    feature_names = cont_features + other_features
    importance = pd.DataFrame({
        'feature': feature_names,
        'coefficient': model.named_steps['regressor'].coef_
    })
    importance['abs_importance'] = abs(importance['coefficient'])
    importance = importance.sort_values('abs_importance', ascending=False)
    print("\nTop 10 most important features:")
    print(importance.head(10).to_string(index=False))
    
    return model, metrics, importance

if __name__ == "__main__":
    model, metrics, importance = train_model('data/processed/rent.csv')

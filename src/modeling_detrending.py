# import pandas as pd
# import numpy as np
# from datetime import datetime
# from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import StandardScaler
# import matplotlib.pyplot as plt

# def detrend_prices(input_file, output_file=None):
#     # Načtení dat
#     df = pd.read_csv(input_file, sep=';')
    
#     # Převod data na datetime a číselnou reprezentaci
#     df['date'] = pd.to_datetime(df['date'])
#     df['days_num'] = (df['date'] - df['date'].min()).dt.days
    
#     # Rozdělení proměnných na kontinuální a dummy
#     continuous_features = ['days_num', 'usable_area']
#     dummy_features = [
#         'garage', 'cellar', 'low_energy', 'balcony', 'easy_access',
#         'terrace', 'loggia', 'parking_lots', 'elevator', 'material_brick',
#         'material_panel', 'Prague_1', 'Prague_2', 'Prague_3', 'Prague_4',
#         'Prague_5', 'Prague_6', 'Prague_7', 'Prague_8', 'Prague_9',
#         'floor_ground', 'floor_above_ground', 'status_good', 'status_very_good',
#         'status_before_reconstruction', 'status_after_reconstruction',
#         'status_project', 'status_under_construction', 'kitchen_separately',
#         'ownership_private', 'nonresidential_unit'
#     ]
    
#     # Příprava dat pro regresi
#     X_continuous = df[continuous_features]
#     X_dummy = df[dummy_features]
    
#     # Standardizace pouze kontinuálních proměnných
#     scaler = StandardScaler()
#     X_continuous_scaled = scaler.fit_transform(X_continuous)
#     X_continuous_scaled = pd.DataFrame(X_continuous_scaled, columns=continuous_features)
    
#     # Spojení standardizovaných kontinuálních a dummy proměnných
#     X = pd.concat([X_continuous_scaled, X_dummy], axis=1)
#     y = df['price']
    
#     # Lineární regrese
#     reg = LinearRegression()
#     reg.fit(X, y)
    
#     # Výpočet trendu
#     trend = reg.predict(X)
    
#     # Odstranění trendu (nejnovější den jako referenční hodnota)
#     df['detrended_price'] = df['price'] - trend + df[df["days_num"] == df["days_num"].max()]['price'].mean()
    
#     # Výpočet R² pro hodnocení kvality modelu
#     r2_score = reg.score(X, y)
    
#     # Koeficienty modelu
#     all_features = continuous_features + dummy_features
#     coef_df = pd.DataFrame({
#         'feature': all_features,
#         'coefficient': reg.coef_,
#         'abs_impact': abs(reg.coef_)
#     })
    
#     # Přidání informace o typu proměnné
#     coef_df['variable_type'] = coef_df['feature'].apply(
#         lambda x: 'Kontinuální' if x in continuous_features else 'Dummy'
#     )
    
#     # Seřazení podle absolutní hodnoty vlivu
#     coef_df = coef_df.sort_values('abs_impact', ascending=False)
#     del coef_df['abs_impact']
    
#     # Základní statistiky
#     stats = {
#         'original': {
#             'mean': df['price'].mean(),
#             'median': df['price'].median(),
#             'std': df['price'].std(),
#             'min': df['price'].min(),
#             'max': df['price'].max()
#         },
#         'detrended': {
#             'mean': df['detrended_price'].mean(),
#             'median': df['detrended_price'].median(),
#             'std': df['detrended_price'].std(),
#             'min': df['detrended_price'].min(),
#             'max': df['detrended_price'].max()
#         },
#         'model': {
#             'r2_score': r2_score,
#             'intercept': reg.intercept_
#         }
#     }
    
#     # Vytvoření grafu
#     plt.figure(figsize=(15, 8))
    
#     # Denní průměry pro lepší vizualizaci
#     daily_means = df.groupby('date').agg({
#         'price': 'mean',
#         'detrended_price': 'mean'
#     }).reset_index()
    
#     plt.plot(daily_means['date'], daily_means['price'], 
#              label='Původní ceny', alpha=0.7)
#     plt.plot(daily_means['date'], daily_means['detrended_price'], 
#              label='Detrendované ceny', alpha=0.7)
    
#     plt.title('Vývoj cen nemovitostí v Praze')
#     plt.xlabel('Datum')
#     plt.ylabel('Cena (Kč)')
#     plt.legend()
#     plt.grid(True, alpha=0.3)
#     plt.xticks(rotation=45)
    
#     # Uložení výsledků
#     if output_file:
#         df.to_csv(output_file, sep=';', index=False)
#         plt.savefig(f"{output_file.rsplit('.', 1)[0]}_plot.png", 
#                    bbox_inches='tight', dpi=300)
        
#         # Uložení koeficientů modelu
#         coef_df.to_csv(f"{output_file.rsplit('.', 1)[0]}_coefficients.csv", 
#                       sep=';', index=False)
    
#     return df, stats, coef_df, plt.gcf()

# if __name__ == "__main__":
#     df, stats, coef_df, fig = detrend_prices('data/processed/sale.csv', 'data/processed/detrended_sale_multivariate.csv')
    
#     print("\nStatistiky původních cen:")
#     for key, value in stats['original'].items():
#         print(f"{key}: {value:,.2f} Kč")
        
#     print("\nStatistiky detrendovaných cen:")
#     for key, value in stats['detrended'].items():
#         print(f"{key}: {value:,.2f} Kč")
    
#     print(f"\nKvalita modelu (R²): {stats['model']['r2_score']:.4f}")
    
#     print("\nNejvýznamnější faktory ovlivňující cenu:")
#     print("\nKontinuální proměnné:")
#     print(coef_df[coef_df['variable_type'] == 'Kontinuální'].to_string(index=False))
#     print("\nDummy proměnné (top 10):")
#     print(coef_df[coef_df['variable_type'] == 'Dummy'].head(10).to_string(index=False))
    
#     plt.show()
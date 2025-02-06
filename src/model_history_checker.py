import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import glob

class HistoryChecker:
    def __init__(self) -> None:
        pass
        
    def check_model_history(self, check_sale: bool = False, check_rent: bool = False) -> None:
        """
        It checks when model updates were made.
        Model updates are made together with the "deleted_listings_..." dataset updates.
        Therefore, we check the dataset "deleted_listings_..." and additionally we check when the last scraping was done, because the data from here is not yet in the dataset "deleted_listings_...".
        """

        x = 7     # Updating interval in days

        # Loading data
        if check_sale:
            df = pd.read_csv("data/processed/sale.csv", sep=';')
            last_scraping = pd.read_json("last_scraping_for_modeling/sale.json")
        if check_rent:
            df = pd.read_csv("data/processed/rent.csv", sep=';')
            last_scraping = pd.read_json("last_scraping_for_modeling/rent.json")

        # Timestamp to date
        df['date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
        last_scraping['date'] = pd.to_datetime(last_scraping['timestamp']).dt.strftime('%Y-%m-%d')

        # Width of the graph
        min_date = pd.to_datetime(df['date']).min()
        max_date = pd.to_datetime(last_scraping['date']).max()
        blue_line = max_date - min_date
        days_difference = (pd.to_datetime('today').normalize() - max_date).days
        max_date = max_date + pd.DateOffset(days=max(x, days_difference))
        red_line = max_date - min_date

        # Time series
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
        all_dates_df = pd.DataFrame({'date': all_dates.strftime('%Y-%m-%d')})

        # Number of advertisements
        daily_counts = df.groupby('date').size().reset_index(name='count')

        # Merge with time series
        daily_counts = pd.merge(all_dates_df, daily_counts, on='date', how='left')
        daily_counts['count'] = daily_counts['count'].fillna(0)

        # Graph
        plt.figure(figsize=(13, 6))
        plt.bar(range(len(daily_counts)), daily_counts['count'], color='blue')
        plt.ylim(0, max(daily_counts['count']) * 1.1)

        max_bar_size = daily_counts['count'].max()

        # Title
        if check_sale:
            plt.title('\nSALES - History of model updates\nThe number of advertisements that no longer appeared on the website during the next scraping\n')
        if check_rent:
            plt.title('\nRENTS - History of model updates\nThe number of advertisements that no longer appeared on the website during the next scraping\n')
        plt.xticks([])

        # Dates
        for i, row in daily_counts.iterrows():
            if row['count'] > 0 or i == blue_line.days or i == red_line.days:
                plt.text(i, -(max_bar_size/20), row['date'], rotation=90, ha='center', va='top')

        # Values above bars
        for i, v in enumerate(daily_counts['count']):
            if v > 0:
                plt.text(i, v+max_bar_size/30, str(int(v)), ha='center')

        # Blue line - last scraping
        plt.axvline(x=daily_counts[daily_counts['date'] == last_scraping['date'].max()].index[0], color='blue')
        plt.text(x=daily_counts[daily_counts['date'] == last_scraping['date'].max()].index[0], y=max_bar_size/20, s="last model update", rotation=90, ha='right', va='bottom')

        # Red line - recommended update
        plt.axvline(x=daily_counts[daily_counts['date'] == max_date.strftime('%Y-%m-%d')].index[0], color='red')
        plt.text(x=daily_counts[daily_counts['date'] == max_date.strftime('%Y-%m-%d')].index[0], y=max_bar_size/20, s="model update recommendation", rotation=90, ha='right', va='bottom')

        plt.tight_layout()
        plt.show()

        print("Graph of model updates was created.")


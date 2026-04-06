import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


def clean_dataframe(df):
    
    current_date = datetime.now()
    original_rows = len(df)
    
    # 1. Remove future dates
    df = df[df['tpep_pickup_datetime'] <= current_date]
    df = df[df['tpep_dropoff_datetime'] <= current_date]
    
    # 2. Pickup before dropoff
    df = df[df['tpep_pickup_datetime'] < df['tpep_dropoff_datetime']]
    
    # 3. Trip duration <= 24 hours
    duration_hours = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 3600
    df = df[duration_hours <= 24]
    
    # 4. Drop missing locations
    df = df.dropna(subset=['PULocationID', 'DOLocationID'])
    df['PULocationID'] = df['PULocationID'].astype(int)
    df['DOLocationID'] = df['DOLocationID'].astype(int)
    
    # 5. Passenger count: ONLY fix 0 and > 6 (keeping nulls as null)
    median_pass = df['passenger_count'].median()  # pandas ignores nulls automatically
    df.loc[df['passenger_count'] == 0, 'passenger_count'] = median_pass
    df.loc[df['passenger_count'] > 6, 'passenger_count'] = median_pass
    # NULL values stay NULL (we'll handle in EDA)
    
    # 6. Negative Fare 
    df = df[df['fare_amount'] > 0]
    
    # 7. Distance between 0 and 100 miles
    df = df[(df['trip_distance'] > 0) & (df['trip_distance'] <= 100)]
    
    # 8. Remove duplicates
    df = df.drop_duplicates()
    
    print(f"Cleaning complete: {len(df):,} rows retained ({len(df)/original_rows*100:.1f}%)")
    return df
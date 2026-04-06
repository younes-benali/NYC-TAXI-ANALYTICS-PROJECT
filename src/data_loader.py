# download_2025_data.py

import os
import urllib.request
from pathlib import Path

# Create the raw data directory if it doesn't exist
RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Base URL for 2025 Yellow Taxi Parquet files
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-"

# All months (01 to 12)
months = [f"{i:02d}" for i in range(1, 13)]

def download_file(month):
    """Download a single month's file if not already present."""
    url = f"{BASE_URL}{month}.parquet"
    dest = RAW_DATA_DIR / f"yellow_tripdata_2025-{month}.parquet"
    
    if dest.exists():
        print(f"  Already exists: {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
        return
    
    print(f" Downloading {month} ... ", end="", flush=True)
    try:
        urllib.request.urlretrieve(url, dest)
        size_mb = dest.stat().st_size / 1e6
        print(f" Done ({size_mb:.1f} MB)")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f" Not available yet (404)")
        else:
            print(f" HTTP {e.code}")
    except Exception as e:
        print(f" Error: {e}")

# Run downloads
print(" Downloading 2025 NYC Yellow Taxi data...\n")
for month in months:
    download_file(month)

print("\n All available months downloaded into 'data/raw/'")
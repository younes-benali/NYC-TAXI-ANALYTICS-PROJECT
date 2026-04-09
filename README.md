# 🚕 NYC Yellow Taxi Analytics Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nyc-taxi-analytics-project-younes-bnl.streamlit.app/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**End-to-end data science project** analyzing 44+ million NYC Yellow Taxi trips (2025) – from raw data ingestion to an interactive dashboard. Built with Pandas, XGBoost, LSTM, Isolation Forest, and Streamlit.

🔗 **Live Demo**:         [Streamlit Cloud App](https://nyc-taxi-analytics-project-younes-bnl.streamlit.app/)  
📊 **GitHub Repository**: [younes-benali/NYC-TAXI-ANALYTICS-PROJECT](https://github.com/younes-benali/NYC-TAXI-ANALYTICS-PROJECT)

---

## 📌 Project Overview

This project demonstrates the full machine learning lifecycle on a real‑world, large‑scale dataset. Key steps include:

- **Data Ingestion** – 12 months of raw Parquet files (50+ GB) from the NYC TLC.
- **Data Cleaning** – Handling missing values, outliers, future dates, and logical inconsistencies.
- **Exploratory Data Analysis (EDA)** – Univariate, temporal, geographic, and behavioral analysis.
- **Feature Engineering** – 22+ features (time‑based, trip dynamics, geographic aggregates, lag features).
- **Modeling** – Four production‑ready models:
  - **Fare Prediction** (XGBoost, R² = 0.94, MAE = $2.03)
  - **Tip Prediction** (binary classifier + conditional regression)
  - **Anomaly Detection** (Isolation Forest – flags unusual trips)
  - **Demand Forecasting** (LSTM – hourly trip volume, MAE ≈ 5 trips/hour)
- **Deployment** – Interactive Streamlit dashboard with live predictions and visualizations.
---
## 🚀 Features of the Dashboard

The Streamlit app (deployed on Streamlit Cloud) provides five interactive tabs:

| Tab | Description |
|-----|-------------|
| **📊 Overview** | Key statistics, daily trip volume, top pickup zones (with date / zone / payment filters) |
| **💰 Fare Predictor** | User inputs trip details → XGBoost model predicts the fare amount in real time |
| **📈 Demand Forecast** | Select a zone → LSTM forecasts the next hour’s trip count using the last 24 hours of data |
| **⚠️ Anomaly Explorer** | Enter fare, distance, duration, tip → Isolation Forest classifies the trip as normal / anomalous |
| **🔍 Data Explorer** | Filter and browse the sample trip data (100k rows) |

All models are pre‑trained and loaded from the `Models/` folder.

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| **Data Processing** | Pandas, NumPy, Dask |
| **Visualization** | Matplotlib, Seaborn, Plotly |
| **Machine Learning** | Scikit‑learn, XGBoost, TensorFlow / Keras (LSTM) |
| **Anomaly Detection** | Isolation Forest |
| **Dashboard** | Streamlit, Plotly |
| **Deployment** | Streamlit Cloud, Git LFS |

---

## 📈 Model Performance Summary

| Model | Target | Algorithm | Key Metric |
|-------|--------|-----------|-------------|
| Fare Prediction | `fare_amount` | XGBoost | MAE = $2.03, R² = 0.94 |
| Tip Prediction (binary) | `will_tip` | XGBoost Classifier | F1 = 0.78 |
| Tip Amount (regression) | `tip_amount` (if tip > 0) | XGBoost Regressor | MAE = $1.25 |
| Anomaly Detection | outlier flag | Isolation Forest | ~1% trips flagged as anomalies |
| Demand Forecasting | hourly `trip_count` | LSTM | MAE ≈ 5 trips/hour (busy zones) |

---
## 📁 Project File Structure & Key Code

Every step of the pipeline is implemented in the following files:

### 1. Data Acquisition & Download
| File | Description |
|------|-------------|
| [`scripts/download_2025_data.py`](src/data_loader.py) | Downloads 12 months of raw Parquet files from NYC TLC website |

### 2. Data Cleaning
| File | Description |
|------|-------------|
| [`src/clean.py`](src/clean.py) | Functions for removing outliers, fixing dates, handling missing values |
| [`notebooks/01_data_cleaning.ipynb`](notebooks/01_data_cleaning.ipynb) | Step‑by‑step cleaning applied to the full dataset |

### 3. Exploratory Data Analysis (EDA)
| File | Description |
|------|-------------|
| [`notebooks/02_EDA_part-1.ipynb`](notebooks/02_EDA_part-1.ipynb) | Univariate analysis, fare/tip/distance distributions, temporal patterns |
| [`notebooks/03_EDA_part-2.ipynb`](notebooks/03_EDA_part-2.ipynb) | Geographic analysis, payment behavior, correlations, outlier investigation |

### 4. Feature Engineering
| File | Description |
|------|-------------|
| [`notebooks/03_feature_engineering.ipynb`](notebooks/03_feature_engineering.ipynb) | End‑to‑end feature engineering on the 10% sample |

### 5. Model Training
| File | Description |
|------|-------------|
| [`notebooks/04_fare_prediction.ipynb`](notebooks/04_fare_prediction.ipynb) | Fare prediction (XGBoost, evaluation) |
| [`notebooks/05_demand_forecasting.ipynb`](notebooks/05_demand_forecasting.ipynb) | LSTM for hourly trip demand |
| [`notebooks/06_anomaly_detection.ipynb`](notebooks/06_anomaly_detection.ipynb) | Isolation Forest for anomaly detection |

### 6. Saved Models & Scalers
| File | Description |
|------|-------------|
| [`Models/xgboost_fare_model.pkl`](Models/xgboost_fare_model.pkl) | Trained XGBoost fare predictor |
| [`Models/isolation_forest_anomaly.pkl`](Models/isolation_forest_anomaly.pkl) | Trained Isolation Forest model |
| [`Models/lstm_zone_*.h5`](Models/) | LSTM models for top 5 zones |
| [`Models/scaler_*.pkl`](Models/) | StandardScaler objects for each model |

### 7. Dashboard & Deployment
| File | Description |
|------|-------------|
| [`app/streamlit_app.py`](app/streamlit_app.py) | Main Streamlit dashboard (5 interactive tabs) |
| [`app/requirements.txt`](app/requirements.txt) | Dashboard‑specific dependencies |
| [`requirements.txt`](requirements.txt) | Core project dependencies |


### 8. Data (Sample only – required for the app)
| File | Description |
|------|-------------|
| [`data/processed/eda_sample_1.2M.parquet`](data/processed/eda_sample_1.2M.parquet) | 1.2M trip sample for visualizations |
| [`data/processed/forcasting_data.parquet`](data/processed/forcasting_data.parquet) | Hourly aggregated demand data |
| [`data/external/taxi_zones/taxi_zone_lookup.csv`](data/external/taxi_zones/taxi_zone_lookup.csv) | Zone ID to name/borough mapping |





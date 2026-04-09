# app/streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import joblib
from tensorflow.keras.models import load_model
import os

# -------------------------------
# PAGE CONFIGURATION
st.set_page_config(page_title="NYC Taxi Analytics", layout="wide", page_icon="🚕")

# -------------------------------
# PATH HELPER – for Streamlit Cloud (repo root is one level above 'app')
def get_project_root():
    """Return absolute path to project root (where 'Models' and 'data' folders live)."""
    current_dir = os.path.dirname(os.path.abspath(__file__))  # .../app
    project_root = os.path.dirname(current_dir)               # .../NYC-TAXI-ANALYTICS-PROJECT
    return project_root

PROJECT_ROOT = get_project_root()
MODELS_DIR = os.path.join(PROJECT_ROOT, "Models")
DATA_PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
DATA_EXTERNAL_DIR = os.path.join(PROJECT_ROOT, "data", "external", "taxi_zones")

# -------------------------------
# CACHE DATA AND MODELS

@st.cache_resource
def load_models():
    """Load all models and scalers using local paths (repo is cloned)."""
    models = {}
    # XGBoost fare model
    xgb_path = os.path.join(MODELS_DIR, "xgboost_fare_model.pkl")
    models['xgb'] = joblib.load(xgb_path)

    # Isolation Forest anomaly detector
    iso_path = os.path.join(MODELS_DIR, "isolation_forest_anomaly.pkl")
    iso_scaler_path = os.path.join(MODELS_DIR, "scaler_anomaly.pkl")
    models['iso_forest'] = joblib.load(iso_path)
    models['iso_scaler'] = joblib.load(iso_scaler_path)

    # LSTM models for top zones
    top_zones = {
        132: "JFK Airport",
        237: "Upper East Side South",
        161: "Midtown Center",
        236: "Upper East Side North",
        186: "Penn Station/Madison Sq West"
    }
    models['lstm'] = {}
    models['lstm_scaler'] = {}
    for zone_id in top_zones.keys():
        model_path = os.path.join(MODELS_DIR, f"lstm_zone_{zone_id}.h5")
        scaler_path = os.path.join(MODELS_DIR, f"scaler_zone_{zone_id}.pkl")
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            model = load_model(model_path, compile=False)
            model.compile(optimizer='adam', loss='mae')
            models['lstm'][zone_id] = model
            models['lstm_scaler'][zone_id] = joblib.load(scaler_path)
    return models

@st.cache_data
def load_sample_data():
    """Load the EDA sample (1.2M rows)."""
    sample_path = os.path.join(DATA_PROCESSED_DIR, "eda_sample_1.2M.parquet")
    df = pd.read_parquet(sample_path)
    # Downsample for performance (100k rows)
    df = df.sample(min(100000, len(df)), random_state=42)
    return df

@st.cache_data
def load_zone_lookup():
    """Load taxi zone lookup CSV."""
    zone_path = os.path.join(DATA_EXTERNAL_DIR, "taxi_zone_lookup.csv")
    return pd.read_csv(zone_path)

# -------------------------------
# MAIN APP
def main():
    st.title("🚕 NYC Yellow Taxi Analytics Platform")
    st.markdown("Predict fares, forecast demand, and detect anomalies using machine learning.")

    with st.spinner("Loading models and data..."):
        models = load_models()
        df_sample = load_sample_data()
        zones = load_zone_lookup()

    tabs = st.tabs(["📊 Overview", "💰 Fare Predictor", "📈 Demand Forecast", "⚠️ Anomaly Explorer", "🔍 Data Explorer"])

    # ---------- TAB 1: OVERVIEW ----------
    with tabs[0]:
        st.header("Key Statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Trips (sample)", f"{len(df_sample):,}")
        col2.metric("Avg Fare", f"${df_sample['fare_amount'].mean():.2f}")
        col3.metric("Avg Tip", f"${df_sample['tip_amount'].mean():.2f}")
        col4.metric("Avg Distance", f"{df_sample['trip_distance'].mean():.1f} mi")

        st.subheader("Daily Trip Volume (Sample)")
        df_sample['date'] = df_sample['tpep_pickup_datetime'].dt.date
        daily = df_sample.groupby('date').size().reset_index(name='count')
        fig = px.line(daily, x='date', y='count', title="Trips per Day")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top 10 Pickup Zones")
        top_zones = df_sample.groupby('PULocationID').size().reset_index(name='count')
        top_zones = top_zones.merge(zones[['LocationID', 'Zone']], left_on='PULocationID', right_on='LocationID')
        top_zones = top_zones.nlargest(10, 'count')
        fig = px.bar(top_zones, x='Zone', y='count', title="Trip Count by Pickup Zone")
        st.plotly_chart(fig, use_container_width=True)

        # ----- Additional Visualizations -----
        st.subheader("Fare Distribution")
        fig_fare = px.histogram(df_sample, x='fare_amount', nbins=50, title="Distribution of Fare Amounts",
                                labels={'fare_amount': 'Fare ($)'}, template='plotly_dark')
        st.plotly_chart(fig_fare, use_container_width=True)

        col_left, col_mid, col_right = st.columns(3)
        with col_left:
            st.subheader("Trips by Hour")
            hourly = df_sample.groupby('pickup_hour').size().reset_index(name='count')
            fig_hour = px.bar(hourly, x='pickup_hour', y='count', title="Hourly Trip Volume",
                              labels={'pickup_hour': 'Hour', 'count': 'Trips'}, template='plotly_dark')
            st.plotly_chart(fig_hour, use_container_width=True)

        with col_mid:
            st.subheader("Payment Type")
            payment_counts = df_sample['payment_type'].map({1:'Credit',2:'Cash',3:'No charge',4:'Dispute',5:'Unknown'}).value_counts()
            fig_payment = px.pie(values=payment_counts.values, names=payment_counts.index, title="Payment Type Share", template='plotly_dark')
            st.plotly_chart(fig_payment, use_container_width=True)

        with col_right:
            st.subheader("Tip Percentage Distribution")
            # Compute tip percentage (avoid division by zero)
            tip_pct = (df_sample['tip_amount'] / df_sample['fare_amount']) * 100
            tip_pct = tip_pct.replace([np.inf, -np.inf], np.nan).dropna()
            fig_tip = px.histogram(x=tip_pct, nbins=40, title="Tip % of Fare",
                                   labels={'x': 'Tip (%)'}, template='plotly_dark')
            st.plotly_chart(fig_tip, use_container_width=True)

        st.subheader("Trip Distance vs Fare")
        scatter_df = df_sample.sample(min(5000, len(df_sample)), random_state=42)
        fig_scatter = px.scatter(scatter_df, x='trip_distance', y='fare_amount', opacity=0.5,
                                 title="Distance vs Fare", labels={'trip_distance': 'Distance (mi)', 'fare_amount': 'Fare ($)'},
                                 template='plotly_dark')
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Optional: Hourly heatmap (day of week vs hour)
        st.subheader("Trip Volume Heatmap (Hour vs Day of Week)")
        df_sample['dayofweek'] = df_sample['tpep_pickup_datetime'].dt.dayofweek
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        heatmap_data = df_sample.groupby(['dayofweek', 'pickup_hour']).size().unstack(fill_value=0)
        heatmap_data.index = [day_names[i] for i in heatmap_data.index]
        fig_heatmap = px.imshow(heatmap_data, labels=dict(x="Hour of Day", y="Day of Week", color="Trips"),
                                title="Hourly Trip Volume by Day of Week", template='plotly_dark', aspect="auto")
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # ---------- TAB 2: FARE PREDICTOR ----------
    with tabs[1]:
        st.header("Predict Taxi Fare")
        st.markdown("Enter trip details below to get an estimated fare.")

        col1, col2 = st.columns(2)
        with col1:
            passenger_count = st.number_input("Passenger count", min_value=1, max_value=6, value=1, key="fare_passenger")
            trip_distance = st.number_input("Trip distance (miles)", min_value=0.1, max_value=100.0, value=2.5, key="fare_distance")
            pickup_hour = st.slider("Pickup hour (0-23)", 0, 23, 14, key="fare_hour")
            is_weekend = st.selectbox("Weekend?", [0, 1], format_func=lambda x: "Yes" if x else "No", key="fare_weekend")
            
            # Zone selection
            zone_list = zones[['LocationID', 'Zone']].drop_duplicates().sort_values('Zone')
            zone_options = dict(zip(zone_list['Zone'], zone_list['LocationID']))
            pickup_zone_name = st.selectbox("Pickup zone", list(zone_options.keys()), key="fare_pickup_zone")
            dropoff_zone_name = st.selectbox("Dropoff zone", list(zone_options.keys()), key="fare_dropoff_zone")
            pickup_zone_id = zone_options[pickup_zone_name]
            dropoff_zone_id = zone_options[dropoff_zone_name]
            
        with col2:
            payment_type = st.selectbox("Payment type", options=[1,2,3,4,5], format_func=lambda x: {1:"Credit",2:"Cash",3:"No charge",4:"Dispute",5:"Unknown"}[x], key="fare_payment")
            ratecode = st.selectbox("Rate code", options=[1,2,3,4,5,6], format_func=lambda x: {1:"Standard",2:"JFK",3:"Newark",4:"Nassau/Westchester",5:"Negotiated",6:"Group"}[x], key="fare_ratecode")
            congestion = st.number_input("Congestion surcharge", min_value=0.0, max_value=10.0, value=2.5, key="fare_congestion")
            cbd_fee = st.number_input("CBD congestion fee", min_value=0.0, max_value=10.0, value=0.0, key="fare_cbd")

        if st.button("Predict Fare", key="fare_predict_btn"):
            input_df = pd.DataFrame([{
                'passenger_count': passenger_count,
                'trip_distance': trip_distance,
                'PULocationID': pickup_zone_id,
                'DOLocationID': dropoff_zone_id,
                'pickup_hour': pickup_hour,
                'is_weekend': is_weekend,
                'congestion_surcharge': congestion,
                'cbd_congestion_fee': cbd_fee,
                'Airport_fee': 0.0,
                'payment_type': payment_type,
                'RatecodeID': ratecode
            }])
            
            # Feature engineering (must match training)
            input_df['is_rush_hour'] = ((input_df['pickup_hour'].between(7,9)) | (input_df['pickup_hour'].between(17,19)) & (input_df['is_weekend'] == 0)).astype(int)
            input_df['is_night'] = (input_df['pickup_hour'].between(22,23) | input_df['pickup_hour'].between(0,5)).astype(int)
            input_df['pickup_month'] = 1
            input_df['pickup_dayofweek'] = 0
            
            # One-hot encode payment_type
            payment_dummies = pd.get_dummies(input_df['payment_type'], prefix='payment')
            for col in ['payment_1','payment_2','payment_3','payment_4']:
                if col not in payment_dummies.columns:
                    payment_dummies[col] = 0
            input_df = pd.concat([input_df, payment_dummies], axis=1)
            
            # One-hot encode RatecodeID
            rate_dummies = pd.get_dummies(input_df['RatecodeID'], prefix='ratecode')
            for col in ['ratecode_1.0','ratecode_2.0','ratecode_3.0','ratecode_4.0','ratecode_5.0','ratecode_6.0']:
                if col not in rate_dummies.columns:
                    rate_dummies[col] = 0
            input_df = pd.concat([input_df, rate_dummies], axis=1)
            
            feature_cols = [
                'passenger_count', 'trip_distance', 'PULocationID', 'DOLocationID',
                'pickup_hour', 'pickup_dayofweek', 'pickup_month', 'is_weekend',
                'is_rush_hour', 'is_night', 'congestion_surcharge', 'cbd_congestion_fee',
                'Airport_fee', 'payment_1', 'payment_2', 'payment_3', 'payment_4',
                'ratecode_1.0', 'ratecode_2.0', 'ratecode_3.0', 'ratecode_4.0',
                'ratecode_5.0', 'ratecode_6.0'
            ]
            for col in feature_cols:
                if col not in input_df.columns:
                    input_df[col] = 0
            X_input = input_df[feature_cols]
            
            pred = models['xgb'].predict(X_input)[0]
            st.success(f"💰 Estimated fare: **${pred:.2f}**")

    # ---------- TAB 3: DEMAND FORECAST ----------
    with tabs[2]:
        st.header("Hourly Demand Forecast")
        zone_options = {132: "JFK Airport", 237: "Upper East Side South", 161: "Midtown Center", 236: "Upper East Side North", 186: "Penn Station/Madison Sq West"}
        selected_zone_name = st.selectbox("Select a pickup zone", list(zone_options.values()), key="demand_zone")
        zone_id = [k for k, v in zone_options.items() if v == selected_zone_name][0]

        model_path = os.path.join(MODELS_DIR, f"lstm_zone_{zone_id}.h5")
        scaler_path = os.path.join(MODELS_DIR, f"scaler_zone_{zone_id}.pkl")
        demand_data_path = os.path.join(DATA_PROCESSED_DIR, "forcasting_data.parquet")

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            @st.cache_resource
            def load_zone_model(zone_id):
                model = load_model(model_path, compile=False)
                model.compile(optimizer='adam', loss='mae')
                scaler = joblib.load(scaler_path)
                return model, scaler

            lstm_model, scaler = load_zone_model(zone_id)
            st.write(f"Forecasting demand for **{selected_zone_name}** using LSTM model.")

            if os.path.exists(demand_data_path):
                demand_data = pd.read_parquet(demand_data_path)
                zone_data = demand_data[demand_data['PULocationID'] == zone_id].sort_values('pickup_hour_floor')
                if len(zone_data) >= 24:
                    last_24 = zone_data['trip_count'].iloc[-24:].values
                    last_24_scaled = scaler.transform(last_24.reshape(-1,1)).flatten()
                    X_input = last_24_scaled.reshape(1,24,1)
                    pred_scaled = lstm_model.predict(X_input, verbose=0)
                    pred = scaler.inverse_transform(pred_scaled.reshape(-1,1))[0,0]
                    st.metric("Forecast for next hour", f"{pred:.1f} trips")

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=zone_data['pickup_hour_floor'].iloc[-48:], y=zone_data['trip_count'].iloc[-48:], mode='lines', name='Actual'))
                    next_hour = zone_data['pickup_hour_floor'].iloc[-1] + timedelta(hours=1)
                    fig.add_trace(go.Scatter(x=[next_hour], y=[pred], mode='markers', name='Forecast', marker=dict(size=10, color='red')))
                    fig.update_layout(title="Last 48 Hours Actual + Next Hour Forecast", xaxis_title="Time", yaxis_title="Trip Count")
                    st.plotly_chart(fig)
                else:
                    st.warning("Not enough historical data for this zone.")
            else:
                st.error(f"Demand data file not found. Expected: {demand_data_path}")
        else:
            st.error(f"LSTM model missing for zone {selected_zone_name}. Expected:\n{model_path}\n{scaler_path}")

    # ---------- TAB 4: ANOMALY EXPLORER ----------
    with tabs[3]:
        st.header("Anomaly Detection")
        st.markdown("Check if a trip is unusual based on its features.")

        col1, col2 = st.columns(2)
        with col1:
            fare = st.number_input("Fare amount ($)", min_value=0.0, max_value=500.0, value=15.0, key="anomaly_fare")
            distance = st.number_input("Trip distance (miles)", min_value=0.0, max_value=100.0, value=3.0, key="anomaly_distance")
            duration = st.number_input("Trip duration (minutes)", min_value=0.0, max_value=300.0, value=15.0, key="anomaly_duration")
        with col2:
            tip = st.number_input("Tip amount ($)", min_value=0.0, max_value=100.0, value=2.0, key="anomaly_tip")
            passenger = st.number_input("Passenger count", min_value=1, max_value=6, value=1, key="anomaly_passenger")

        if st.button("Check Anomaly", key="anomaly_btn"):
            speed = distance / (duration/60) if duration > 0 else 0
            feature_cols = ['fare_amount', 'tip_amount', 'trip_distance', 'trip_duration_min', 'trip_speed_mph',
                            'passenger_count', 'congestion_surcharge', 'cbd_congestion_fee', 'Airport_fee',
                            'extra', 'mta_tax', 'tolls_amount', 'improvement_surcharge']
            input_data = {
                'fare_amount': fare,
                'tip_amount': tip,
                'trip_distance': distance,
                'trip_duration_min': duration,
                'trip_speed_mph': speed,
                'passenger_count': passenger,
                'congestion_surcharge': 2.5,
                'cbd_congestion_fee': 0.0,
                'Airport_fee': 0.0,
                'extra': 0.5,
                'mta_tax': 0.5,
                'tolls_amount': 0.0,
                'improvement_surcharge': 1.0
            }
            X = pd.DataFrame([input_data])[feature_cols]
            X_scaled = models['iso_scaler'].transform(X)
            pred = models['iso_forest'].predict(X_scaled)[0]
            score = models['iso_forest'].score_samples(X_scaled)[0]
            if pred == -1:
                st.error(f"🚨 Anomaly detected! Anomaly score: {score:.2f}")
            else:
                st.success(f"✅ Normal trip. Anomaly score: {score:.2f}")

    # ---------- TAB 5: DATA EXPLORER ----------
    with tabs[4]:
        st.header("Explore Raw Data")
        st.markdown("Filter and view sample trips.")
        col1, col2 = st.columns(2)
        with col1:
            min_date = df_sample['tpep_pickup_datetime'].min().date()
            max_date = df_sample['tpep_pickup_datetime'].max().date()
            date_range = st.date_input("Date range", [min_date, max_date], key="data_date_range")
        with col2:
            zones_list = zones['Zone'].unique()
            selected_zone = st.selectbox("Pickup zone", ["All"] + list(zones_list), key="data_zone")

        filtered = df_sample.copy()
        if len(date_range) == 2:
            start, end = date_range
            filtered = filtered[(filtered['tpep_pickup_datetime'].dt.date >= start) & (filtered['tpep_pickup_datetime'].dt.date <= end)]
        if selected_zone != "All":
            zone_id = zones[zones['Zone'] == selected_zone]['LocationID'].values[0]
            filtered = filtered[filtered['PULocationID'] == zone_id]

        st.write(f"Showing {len(filtered)} trips")
        st.dataframe(filtered.head(100))

if __name__ == "__main__":
    main()

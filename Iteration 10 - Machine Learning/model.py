from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import logging
import os
import numpy as np
import joblib
import json
from datetime import datetime, timedelta

# Create necessary directories
os.makedirs('./logging', exist_ok=True)
os.makedirs('./models', exist_ok=True)
logging.basicConfig(filename='./logging/logging.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("my_logger")

# Load your weather data
weather_df = pd.DataFrame()
try:
    # Use SQLAlchemy to connect to the database
    engine = create_engine(f'sqlite:///{"weather.db"}')
    
    # Query all numeric columns for potential use in the models
    column_list = """
    location, min_temp, max_temp, rainfall, evaporation, sunshine, 
    wind_gust_speed, windspeed9am, windspeed3pm, humidity9am, humidity3pm, 
    pressure9am, pressure3pm, cloud9am, cloud3pm, 
    temp9am, temp3pm, rain_tomorrow
    """
    weather_df = pd.read_sql(f'SELECT {column_list} FROM weather', engine)

    # Update your column mapping to match the actual database column names
    column_mapping = {
        'location': 'Location',
        'min_temp': 'MinTemp',
        'max_temp': 'MaxTemp',
        'rainfall': 'Rainfall',
        'evaporation': 'Evaporation',
        'sunshine': 'Sunshine',
        'wind_gust_speed': 'WindGustSpeed',
        'windspeed9am': 'WindSpeed9am',
        'windspeed3pm': 'WindSpeed3pm',
        'humidity9am': 'Humidity9am',
        'humidity3pm': 'Humidity3pm',
        'pressure9am': 'Pressure9am',
        'pressure3pm': 'Pressure3pm',
        'cloud9am': 'Cloud9am',
        'cloud3pm': 'Cloud3pm',
        'temp9am': 'Temp9am',
        'temp3pm': 'Temp3pm',
        'rain_tomorrow': 'RainTomorrow'
    }
    
    # Rename columns as needed
    for old_name, new_name in column_mapping.items():
        if old_name in weather_df.columns:
            weather_df = weather_df.rename(columns={old_name: new_name})
except sqlite3.Error as e:
    logger.error(f"SQLite error: {e}")
except Exception as e:
    logger.error(f"Error reading from database: {e}")


# Get unique location values
locations = weather_df['Location'].unique()

# Dictionary to store DataFrames for each location
location_dfs = {}

# Dictionary to store columns available for each location after filtering
location_columns = {}

threshold = 30.0
# Split the data by location and store in dictionary
for location in locations:
    # Filter data for this location
    location_dfs[location] = weather_df[weather_df['Location'] == location].copy()
    
    # Remove the Location column since it's now redundant
    location_dfs[location] = location_dfs[location].drop(columns=['Location'])
    
    # Handle missing values by dropping columns if more than threshold% of the data is missing
    missing_percentage = location_dfs[location].isna().mean() * 100
    columns_to_drop = missing_percentage[missing_percentage > threshold].index.tolist()
    location_dfs[location] = location_dfs[location].drop(columns=columns_to_drop)
    
    # Fill missing values with linear interpolation
    location_dfs[location] = location_dfs[location].interpolate(method='linear')
    
    # Store the columns available for this location after filtering
    location_columns[location] = location_dfs[location].columns.tolist()
    
    print(f"Created DataFrame for {location} with {len(location_dfs[location])} rows and {len(location_columns[location])} columns")
    
    # Print which columns were dropped due to missing data
    all_possible_cols = set(weather_df.columns) - {'Location'}
    dropped_cols = all_possible_cols - set(location_columns[location])
    if dropped_cols:
        print(f"  Columns dropped for {location} due to missing data: {', '.join(dropped_cols)}")

# Initialize metadata dictionary
model_metadata = {}

# Train multivariate models for each location
for location, df in location_dfs.items():
    print(f"\nTraining multivariate model for {location}...")
    
    # Get all model features (excluding target variable if present)
    all_cols = location_columns[location].copy()
    if 'RainTomorrow' in all_cols:
        all_cols.remove('RainTomorrow')
    
    # Skip location if not enough columns remain after filtering
    if len(all_cols) < 2:
        print(f"  WARNING: Not enough columns for {location} after filtering. Skipping.")
        continue
    
    # Store metadata for this location
    model_metadata[location] = {
        'available_columns': all_cols,
        'db_column_mapping': {col: next((k for k, v in column_mapping.items() if v == col), None) for col in all_cols},
        'n_lags': 14,  # Use 14 days of history
        'model_path': f'./models/{location}_multivariate_forecaster.joblib',
        'train_stats': {
            col: {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max())
            } for col in all_cols
        }
    }
    
    # Prepare data for multivariate forecasting using 14 days of history
    n_lags = 14
    X_multi = []
    y_multi = []
    
    # For each possible window in the dataset
    for i in range(n_lags, len(df)):
        # Get the window of 14 days for all features
        window_data = df[all_cols].iloc[i-n_lags:i].values.flatten()
        
        # The target is the next day's values for all features
        target = df[all_cols].iloc[i].values
        
        X_multi.append(window_data)
        y_multi.append(target)
    
    # Convert to numpy arrays
    X_multi = np.array(X_multi)
    y_multi = np.array(y_multi)
    
    print(f"  Training on {len(X_multi)} samples with {X_multi.shape[1]} features to predict {len(all_cols)} outputs")
    print(f"  Using columns: {', '.join(all_cols)}")
    
    try:
        # Train multivariate random forest model
        multi_forecaster = RandomForestRegressor(n_estimators=100, n_jobs=-1, random_state=42)
        multi_forecaster.fit(X_multi, y_multi)
        
        # Save the model in .joblib format
        joblib.dump(multi_forecaster, model_metadata[location]['model_path'])
        print(f"  Model saved to {model_metadata[location]['model_path']}")
        
    except Exception as e:
        logger.error(f"Error training multivariate model for {location}: {e}")
        print(f"  Error: {e}")

# Save the model metadata to a JSON file
with open('./models/multivariate_model_metadata.json', 'w') as f:
    json.dump(model_metadata, f, indent=2)

# Create a separate utility file for the forecaster class
print("\nMultivariate model training complete!")
print(f"Created models for {len(model_metadata)} locations.")
print("All models are saved in the 'models' directory in .joblib format.")
print("Model metadata is saved to 'models/multivariate_model_metadata.json'.")
print("Use the separate multivariate_forecaster.py file to generate forecasts.")
print("\nExample usage from an external file:")
print("""
from models.multivariate_forecaster import MultivariateForecaster

# Initialize the multivariate forecaster
forecaster = MultivariateForecaster()

# Get available locations
locations = forecaster.get_available_locations()
print(f"Available locations: {locations}")

# Generate a 7-day forecast for all weather variables in Sydney
sydney_forecast = forecaster.forecast('Sydney')

# Print temperature forecasts
print(f"\\n7-day MaxTemp forecast for Sydney:")
for date, value in zip(sydney_forecast['dates'], sydney_forecast['forecasts']['MaxTemp']['values']):
    print(f"  {date}: {value:.1f}°C")

# Print rainfall forecasts
print(f"\\n7-day Rainfall forecast for Sydney:")
for date, value in zip(sydney_forecast['dates'], sydney_forecast['forecasts']['Rainfall']['values']):
    print(f"  {date}: {value:.1f}mm")
""")
